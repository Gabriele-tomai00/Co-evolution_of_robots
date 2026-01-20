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

