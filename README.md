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
├── main.py
├── utils.py
├── arena.py
├── robot.py
├── sensors.py
├── neat_controller.py
├── controllers.py
├── neat_config.txt
├── requirements.txt
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
  - Given a robot and the arena, computes a fixed-size vector of 7 floats (`num_inputs = 7` in `neat_config.txt`):
    1. Normalized distance to the opponent (divided by arena diagonal).
    2. Normalized angle difference to the opponent (divided by PI to be in [-1, 1]).
    3. Normalized health (divided by max health).
    4. Normalized distance to the LEFT wall (divided by arena width).
    5. Normalized distance to the RIGHT wall (divided by arena width).
    6. Normalized distance to the BOTTOM wall (divided by arena height).
    7. Normalized distance to the TOP wall (divided by arena height).

- **Action decoding**
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
   - Creates a `neat.Population`

2. **Evolution loop**
   - Adds NEAT reporters
   - Runs evolution by calling:
     ```python
     winner = population.run(eval_genomes, GENERATIONS)
     ```
   - For each generation:
     - `population.run` calls `eval_genomes`.
     - `eval_genomes` performs competitive co-evolution:
       - Builds networks for each genome.
       - Runs `simulate_battle` for all genome pairs.
       - Updates fitness values based on the battle outcomes.

3. **Selecting the best genome**
   - After all the generations, NEAT returns the best genome (`winner`).
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

## Setup and Execution

### Requirements

- Python `>= 3.9`
- Recommended: virtual environment (venv, conda, etc.)

Python dependencies are listed in `requirements.txt`

### Running the evolutionary experiment

Basic run (minimal console output):

```bash
python main.py
```

Run with detailed NEAT logs:

```bash
python main.py --verbose
```
You can add the following parameter:
- `--generations N`: number of generations to run the experiment (default: 200).
- `--pop-size N`: maximum number of genomes in the population (default: 50).
- 


### Expected outputs

- Console logs of the NEAT evolutionary process for `GENERATIONS` generations.
- Final ASCII table summarizing the best genome (ID, fitness, nodes, connections).
- Saved best genome in:
  - `best_robot.pkl`
- Test phase summary:
  - ASCII table of battles between the best genome and random opponents.
  - Final line summarizing wins and losses of the best controller.

You can later reload `best_robot.pkl` to visualize or reuse the evolved controller in different arenas or experimental setups.