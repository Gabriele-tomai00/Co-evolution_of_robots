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


SLIDES

1) Simulation environment: spiego di cosa si tratta

2) Main classes 1/3: inizio a spiegare le classi principali. IN questa slide ho Arena e Robot

3) Main classes 2/3: Baseline Controller (con Random, Static, Aggressive controller)

4) Main classes 3/3: Sensor, neat.nn.FeedForwardNetwork

5) Sensor and NN: sensori normalizzati, input e ouput

6) fitness calculation: hybrid fitness (internal + external), Fitness function (quando si guadanano punti), i 3 aspetti (vittoria, aggressione, sopravvivenza)

7) Evolutional Cycle: cosa succede per ogni generazione: initial population, co-evolution, external validation, fitness calculation, selection, mutation e crossover, e finisce di nuovo in initial population

8) Final test: il winner contro i Random robots: random static e chaser

9) Some results: qui mostro grafici che confrontano interna ed esterna fitness (diversi grafici in cui ho cambiato il numero di genreazioni, elitismo e numero degli indivdui della popolazione).

# Scaletta Presentazione (15 minuti)

## 1. Introduzione e Obiettivi (2 min)
- **Titolo**: Co-evolution of Robots with NEAT
- **Contesto**: Optimization for Artificial Intelligence
- **Obiettivo**: Studiare la co-evoluzione competitiva tra agenti robotici.
- **Domanda di ricerca**: È possibile evolvere strategie complesse di combattimento (movimento e sparo) partendo da zero senza regole esplicite?

## 2. Methodology: NEAT (NeuroEvolution of Augmenting Topologies) (3 min)

### General Theory
*   **Definition**: Neuroevolution algorithm evolving **weights** and **topology** of the neural network simultaneously.
*   **Mechanism**: Starts from minimal structures (input/output only) and adds nodes/connections via mutations (complexification).
*   **Key Techniques**:
    *   **Speciation**: Divides the population into species to protect new topological innovations from premature competition.
    *   **Historical Markings**: Enables crossover between different topologies without losing information.

### Application in the Project
*   **Start Minimal**: Each robot starts with the simplest possible topology:
    *   **7 Inputs** (Sensors) connected directly to **3 Outputs** (Motors + Cannon).
    *   No hidden nodes ("dumb agents").
*   **Specific Evolution**: 
    *   NEAT adds hidden neurons to process finer strategies (e.g., "if enemy is far BUT health is low -> run away").
    *   Speciation prevents simple but effective strategies (e.g., "spin and shoot randomly") from immediately eliminating more complex but still imperfect attempts.
*   **Advantage**: Compared to a fixed network, NEAT finds the minimal structure needed to win, avoiding overfitting and unnecessary computations.

## 3. L'Ambiente di Simulazione (3 min)
- **Arena 2D**: Spazio limitato, bordi.
- **Robot**:
  - **Sensori (Input: 7)**: Distanza/Angolo avversario, Salute, Distanza muri (4).
  - **Attuatori (Output: 3)**: Muovi (avanti/indietro), Ruota (dx/sx), Spara.
- **Fisica**: Collisioni, proiettili, danni.

## 4. Il Ciclo Evolutivo (3 min)
- **Popolazione**: 50 robot (o variabile).
- **Valutazione (Fitness)**:
  - Combattimenti "Round-Robin" o casuali.
  - **Funzione di Fitness**:
    - +100 per la vittoria.
    - +Danno inflitto.
    - +Sopravvivenza (bonus tempo).
- **Generazioni**: ~15-300 (a seconda dell'esperimento).

## 5. Risultati Sperimentali (2 min)
- Mostrare grafici di fitness (media vs best).
- Analisi del comportamento emergente:
  - Inseguimento.
  - Schivata (se presente).
  - Strategie di sparo.
- Confronto con comportamento casuale (Test finale).

## 6. Conclusioni e Sviluppi Futuri (2 min)
- Sintesi: NEAT è riuscito a evolvere agenti capaci di battere avversari casuali?
- Limitazioni: Tempo di calcolo, possibili loop o stallo.
- Futuro: Ostacoli nell'arena, team co-evolution (2vs2), sensori più complessi (ray casting).

---

# Suggerimento Visualizzazione Ciclo Evolutivo (Slide "Ciclo NEAT")

Per la slide grafica, puoi usare uno schema circolare o a flusso come questo:

1.  **Popolazione Iniziale** (Icona: Gruppo di Robot 🤖)
    *   Reti neurali semplici e casuali.
    *   *Freccia verso...*

2.  **Valutazione / Simulazione** (Icona: Spade incrociate ⚔️ o Arena)
    *   Ogni robot combatte contro tutti gli altri (Round-Robin).
    *   Ogni robot combatte contro Bot Statici/Chaser (Validazione).
    *   *Freccia verso...*

3.  **Calcolo Fitness** (Icona: Grafico a barre 📊 o Medaglia 🥇)
    *   Assegnazione punteggi: Vittorie + Danni inflitti + Sopravvivenza.
    *   *Freccia verso...*

4.  **Selezione e Speciazione** (Icona: Lente d'ingrandimento 🔍 o Filtro)
    *   I robot sono divisi in **Specie** (per somiglianza).
    *   I migliori di ogni specie sopravvivono (Elitismo).
    *   I peggiori vengono eliminati.
    *   *Freccia verso...*

5.  **Riproduzione e Mutazione** (Icona: DNA 🧬)
    *   **Crossover**: Incrocio tra due "genitori" vincenti.
    *   **Mutazione**: 
        *   Cambio pesi.
        *   Aggiunta nuove connessioni.
        *   Aggiunta nuovi nodi.
    *   *Freccia che torna all'inizio (Popolazione / Nuova Generazione)* 🔄

**Nota**: Questo ciclo si ripete per `N` generazioni.

---

# Key NEAT Configuration (Customized)

Here are the most critical hyperparameters tuned for this project:

1.  **`pop_size = 50`**: 
    *   Balanced population size to ensure diversity while keeping simulation time manageable.
2.  **`num_hidden = 0`**: 
    *   Starts with **no hidden nodes** (minimal topology) to let complex strategies emerge naturally only if needed.
3.  **`initial_connection = full`**: 
    *   All 7 sensors are initially connected to all 3 actuators to provide immediate feedback loops.
4.  **`conn_add_prob = 0.5`**: 
    *   High probability (50%) of adding new connections during mutation to encourage rapid structural exploration.
5.  **`compatibility_threshold = 3.0`**: 
    *   Determines how different two genomes must be to belong to different species (controls biodiversity).
6.  **`fitness_criterion = max`**: 
    *   Evolution is driven by maximizing the fitness score (damage inflicted + survival bonus + victory reward).

---

# Project Structure & Classes

Here is a brief overview of the main classes in the project, useful for the "Software Architecture" slide.

### **1. `Arena`** (in `arena.py`)
*   **Role**: Manages the simulation environment.
*   **Responsibilities**:
    *   Defines the 2D boundaries (width, height).
    *   Handles the simulation loop (`step()`).
    *   Enforces physics constraints (keeps robots inside walls).
    *   Calculates damage and detects hits.

### **2. `Robot`** (in `robot.py`)
*   **Role**: Represents a single agent in the arena.
*   **Responsibilities**:
    *   Stores state: position `(x, y)`, `angle`, `health`.
    *   Executes actions: `apply_action()` updates position and orientation based on controller output.
    *   Acts as a physical body, separated from the decision-making logic.

### **3. `Sensors`** (in `sensors.py`)
*   **Role**: The perception layer.
*   **Responsibilities**:
    *   Extracts features from the environment (`get()`).
    *   Computes the **7 inputs** for the neural network:
        *   Distance and Angle to opponent.
        *   Current Health.
        *   Distances to the 4 walls.

### **4. `neat.nn.FeedForwardNetwork` (Library Class)**
*   **Role**: The brain of the evolved robot.
*   **Responsibilities**:
    *   Generated directly by the `neat-python` library from the genome.
    *   **Inputs**: Receives the 7 sensor values.
    *   **Outputs**: Produces 3 raw float values used by `Robot.apply_action`:
        *   `Action[0]`: Move.
        *   `Action[1]`: Turn.
        *   `Action[2]`: Shoot.

### **5. Baseline Controllers** (in `controllers.py`)
*   **Role**: Benchmark opponents for evaluation.
*   **Classes**:
    *   `RandomController`: Moves and shoots completely randomly.
    *   `StaticShooter`: Stands still, rotates towards opponent, and shoots.
    *   `AggressiveChaser`: Moves directly towards opponent and shoots.
