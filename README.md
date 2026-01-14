# Co-evolution_of_robots

Python project for the *Optimization for Artificial Intelligence* exam.

The goal is to study competitive co-evolution using NEAT (NeuroEvolution of Augmenting Topologies).  
Two simulated robots fight in a 2D arena; each robot is controlled by a small neural network evolved with NEAT.  
The evolutionary process tries to produce policies that move, rotate and shoot in order to survive and destroy the opponent.

![alt text](img/robot_movement_and_boundaries.png)

---

## Project Structure

Repository root:

```text
project/
├── main.py              # Entry point, NEAT setup, evolution and final testing
├── utils.py             # Fitness evaluation, battle simulation, helper utilities
├── arena.py             # Arena geometry, rules, damage, termination conditions
├── robot.py             # Robot state (pose, health) and action execution
├── sensors.py           # Sensor model: builds the input vector for the network
├── neat_controller.py   # NEATController (genome → neural net → high-level action)
├── controllers.py       # Example handcrafted controller (RandomController)
├── neat_config.txt      # NEAT configuration (population, mutation, topology, etc.)
├── requirements.txt     # Python dependencies (neat-python, tabulate)
└── README.md
```

Short file summary:
- `main.py` – builds the NEAT configuration, creates the population, runs evolution and tests the best genome.
- `utils.py` – implements `simulate_battle`, `compute_fitness`, `eval_genomes`, and `test_best_genome_against_random_opponents`.
- `arena.py` – defines the 2D arena, step logic, boundary conditions and hit/damage computation.
- `robot.py` – represents a single robot (position, orientation, health, last action).
- `sensors.py` – computes a 7-dimensional sensor vector for each robot (opponent distance/angle, distance from walls, health).
- `neat_controller.py` – wraps a NEAT-evolved neural network and decodes its outputs into a structured action.
- `controllers.py` – contains a simple `RandomController` used as a conceptual baseline.
- `neat_config.txt` – contains all NEAT hyperparameters (population size, topology, mutation rates, species, etc.).

---

## Main Operations

- **Sensor computation (`Sensors.get`)**
  - Given a robot and the arena, computes:
    - Normalized distance to the opponent.
    - Normalized angle difference to the opponent.
    - Normalized health.
    - Normalized distances to the four arena walls.
  - Produces a fixed-size vector of 7 floats, which matches `num_inputs = 7` in `neat_config.txt`.

- **Action decoding (`NEATController.decide`)**
  - Reads the current sensor vector.
  - Feeds it to the NEAT-generated feed-forward network.
  - Interprets the three outputs as:
    - `move` ∈ ℝ: forward/backward motion (−1 = strong backward, +1 = strong forward).
    - `turn` ∈ ℝ: rotation (−1 = left, +1 = right).
    - `shoot` ∈ {False, True}: fire if output[2] > 0.5.

- **Battle simulation (`simulate_battle`)**
  - Instantiates two `Robot` objects with controllers corresponding to two neural networks.
  - Runs the battle for at most `MAX_STEPS` time steps (300 by default).
  - At each step:
    - Computes sensors for both robots.
    - Applies their actions (movement, rotation, shooting).
    - Updates the arena (damage, boundaries, death checks).
  - Stops when at least one robot dies or the step limit is reached.
  - Returns two fitness contributions, one for each controller.

- **Fitness computation (`compute_fitness`)**
  - Strong reward (+100) for winning the fight.
  - Adds damage inflicted by each robot to its fitness.
  - Adds a small bonus proportional to the number of steps survived (encourages longer survival).

- **Genome evaluation (`eval_genomes`)**
  - Required by `neat-python`. For each generation:
    - Initializes all genomes with fitness 0.
    - Builds a neural network for every genome.
    - Plays *round-robin* battles: every pair of genomes fights once.
    - Accumulates fitness from the battles into each genome.

- **Testing the best genome (`test_best_genome_against_random_opponents`)**
  - After evolution, converts the best genome into a network.
  - Samples random opponent genomes from the final population.
  - Simulates several battles and records who wins and the fitness scores.
  - Prints an ASCII table with the summary of test matches.

---

## Program Flow

High-level execution when running `python main.py`:

1. **Initialization (in `main.py`)**
   - Sets a fixed random seed (`random.seed(0)`).
   - Loads NEAT configuration from `neat_config.txt`.
   - Creates a `neat.Population` using:
     - `DefaultGenome`
     - `DefaultReproduction`
     - `DefaultSpeciesSet`
     - `DefaultStagnation`

2. **Evolution loop**
   - Adds NEAT reporters:
     - `StdOutReporter`: controls how much is printed (detailed if `--verbose`).
     - `StatisticsReporter`: collects statistics across generations.
   - Runs evolution by calling:
     ```python
     winner = population.run(eval_genomes, GENERATIONS)
     ```
   - Here `GENERATIONS = 15` (defined in `utils.py`).
   - For each generation:
     - `population.run` calls `eval_genomes`.
     - `eval_genomes` performs competitive co-evolution:
       - Builds networks for each genome.
       - Runs `simulate_battle` for all genome pairs.
       - Updates fitness values based on the battle outcomes.

3. **Selecting the best genome**
   - After 15 generations, NEAT returns the best genome (`winner`).
   - Prints a summary table with:
     - `Genome ID`
     - `Fitness`
     - `Nodes`
     - `Enabled connections`
   - Optionally prints the raw genome structure if `--verbose` is used.
   - Serializes the best genome to `best_robot.pkl` using `pickle`.

4. **Testing phase**
   - Builds a feed-forward network from `winner`.
   - Runs `test_best_genome_against_random_opponents`:
     - Picks random genomes from `population.population`.
     - Simulates battles between `winner_net` and each random opponent.
     - Prints an ASCII table with match index, winner label and fitness scores.
   - Prints a final summary: total wins and losses of the best genome.

Conceptually:

```text
main.py
 └─ NEAT Population
     ├─ eval_genomes (per generation)
     │   └─ simulate_battle (pairwise fights)
     └─ winner genome
         ├─ serialization to best_robot.pkl
         └─ test_best_genome_against_random_opponents
             └─ simulate_battle vs random opponents
```

---

## Important NEAT Parameters

All NEAT hyperparameters are defined in [`neat_config.txt`](./neat_config.txt).  
Below are the most relevant ones for understanding the behavior of the system.

### Global NEAT settings (`[NEAT]`)

| Parameter                | Value   | Meaning                                                                 |
|--------------------------|---------|-------------------------------------------------------------------------|
| `fitness_criterion`      | `max`   | NEAT optimizes for the maximum fitness in the population.              |
| `pop_size`               | `50`    | Number of genomes (robots) per generation.                             |
| `reset_on_extinction`    | `False` | Do not reset the population if all species go extinct.                 |
| `no_fitness_termination` | `False` | Evolution can stop early if threshold is reached.                      |
| `fitness_threshold`      | `200.0` | Stop if the best fitness reaches or exceeds this value.                |
| `GENERATIONS` (code)     | `15`    | Number of generations to run (defined in `utils.py`).                  |

### Genome / Network topology (`[DefaultGenome]`)

| Parameter           | Value | Meaning                                                     |
|---------------------|-------|-------------------------------------------------------------|
| `num_inputs`        | `7`   | Must match the length of the sensor vector.                |
| `num_outputs`       | `3`   | Move, turn, shoot.                                         |
| `num_hidden`        | `0`   | Start with a pure input–output architecture.               |
| `feed_forward`      | `True`| No recurrent connections; strictly feed-forward networks.   |
| `initial_connection`| `full`| Initially connect all inputs to all outputs.               |

### Mutation of weights and structure

| Parameter             | Value | Meaning                                            |
|-----------------------|-------|----------------------------------------------------|
| `weight_mutate_rate`  | `0.8` | Probability to mutate a connection weight.        |
| `weight_mutate_power` | `0.5` | Standard deviation of weight perturbation.        |
| `weight_replace_rate` | `0.1` | Probability to replace weight instead of perturb. |
| `bias_mutate_rate`    | `0.7` | Probability to mutate node biases.                |
| `bias_mutate_power`   | `0.5` | Magnitude of bias mutation.                       |
| `conn_add_prob`       | `0.5` | Probability to add a new connection.              |
| `conn_delete_prob`    | `0.5` | Probability to delete an existing connection.     |
| `node_add_prob`       | `0.2` | Probability to add a new hidden node.             |
| `node_delete_prob`    | `0.2` | Probability to delete a node.                     |

### Speciation, stagnation and reproduction

| Section               | Parameter             | Value | Meaning                                              |
|-----------------------|-----------------------|-------|------------------------------------------------------|
| `[DefaultSpeciesSet]` | `compatibility_threshold` | `3.0` | Distance above which genomes belong to different species. |
| `[DefaultStagnation]` | `max_stagnation`      | `20`  | Species removed if they do not improve for 20 generations. |
| `[DefaultStagnation]` | `species_elitism`     | `2`   | Number of top genomes per species that always survive. |
| `[DefaultReproduction]` | `elitism`          | `2`   | Number of top genomes in the whole population copied unchanged. |
| `[DefaultReproduction]` | `survival_threshold` | `0.2` | Fraction of genomes per species allowed to reproduce. |

These parameters jointly control exploration (mutation, structural changes) and exploitation (elitism, species preservation) of the search space of robot controllers.

---

## Setup and Execution

### Requirements

- Python `>= 3.9`
- Recommended: virtual environment (venv, conda, etc.)

Python dependencies are listed in `requirements.txt`:
- `neat-python>=0.92`
- `tabulate`

### Running the evolutionary experiment

Basic run (minimal console output):

```bash
python main.py
```

Run with detailed NEAT logs:

```bash
python main.py --verbose
```

### Expected outputs

- Console logs of the NEAT evolutionary process for `GENERATIONS` generations.
- Final ASCII table summarizing the best genome (ID, fitness, nodes, connections).
- Saved best genome in:
  - `best_robot.pkl`
- Test phase summary:
  - ASCII table of battles between the best genome and random opponents.
  - Final line summarizing wins and losses of the best controller.

You can later reload `best_robot.pkl` to visualize or reuse the evolved controller in different arenas or experimental setups.
