import neat
import random
import pickle

from arena import Arena
from robot import Robot
from sensors import Sensors


# Maximum number of simulation steps for a single battle
MAX_STEPS = 300

# Number of generations for the evolutionary process
GENERATIONS = 15


def simulate_battle(net1, net2):
    """
    Simulates a fight between two robots controlled by neural networks.
    Returns the fitness contribution for both controllers.
    """

    # Minimal arena: unit square with two robots
    robot1 = Robot(controller=net1, start_pos=(0.2, 0.5))
    robot2 = Robot(controller=net2, start_pos=(0.8, 0.5))
    arena = Arena(width=1.0, height=1.0, robots=[robot1, robot2], max_steps=MAX_STEPS)

    for step in range(MAX_STEPS):
        # Sensor values represent the current state of the environment
        sensors1 = Sensors.get(robot1, arena)
        sensors2 = Sensors.get(robot2, arena)

        # Neural networks compute actions from sensor inputs
        action1 = net1.activate(sensors1)
        action2 = net2.activate(sensors2)

        # Actions modify robot state (movement, shooting, etc.)
        robot1.apply_action(action1)
        robot2.apply_action(action2)

        # Environment update (physics, collisions, damage)
        arena.apply_damage()
        arena.keep_inside(robot1)
        arena.keep_inside(robot2)

        # Battle ends when at least one robot is destroyed
        if robot1.is_dead() or robot2.is_dead():
            break

    return compute_fitness(robot1, robot2, step)


def compute_fitness(robot1, robot2, steps):
    """
    Computes fitness values based on battle outcome.
    Fitness is non-stationary and depends on the opponent behavior.
    """

    fitness1 = 0.0
    fitness2 = 0.0

    # Strong reward for winning the fight
    if robot1.is_dead() and not robot2.is_dead():
        fitness2 += 100.0
    elif robot2.is_dead() and not robot1.is_dead():
        fitness1 += 100.0

    # Reward aggressive and effective behaviors
    fitness1 += robot1.damage_inflicted
    fitness2 += robot2.damage_inflicted

    # Small reward for surviving longer
    fitness1 += steps * 0.1
    fitness2 += steps * 0.1

    return fitness1, fitness2


def eval_genomes(genomes, config):
    """
    Evaluation function required by neat-python.
    Each genome is evaluated by fighting against other genomes.
    """

    # Initialize fitness for all genomes
    for _, genome in genomes:
        genome.fitness = 0.0

    # Create neural networks from genomes
    networks = {}
    for genome_id, genome in genomes:
        # every genome gets its own neural network
        # the netowrk takes sensor inputs and produces action outputs
        networks[genome_id] = neat.nn.FeedForwardNetwork.create(genome, config)

    genome_ids = list(networks.keys())

    # Round-robin competitive coevolution
    for i in range(len(genome_ids)):
        for j in range(i + 1, len(genome_ids)):
            id1 = genome_ids[i]
            id2 = genome_ids[j]

            net1 = networks[id1]
            net2 = networks[id2]

            f1, f2 = simulate_battle(net1, net2)

            # Fitness accumulation reflects relative performance
            genomes[i][1].fitness += f1
            genomes[j][1].fitness += f2


def main():
    # Set random seed for reproducibility, used in genome evaluation
    random.seed(0)

    # Load NEAT configuration (same structure as course notebook)
    config = neat.Config(
        neat.genome.DefaultGenome,
        neat.reproduction.DefaultReproduction,
        neat.species.DefaultSpeciesSet,
        neat.stagnation.DefaultStagnation,
        "neat_config.txt"
    )

    # Initialize population of neural networks
    population = neat.Population(config)

    # Report evolution progress and statistics
    population.add_reporter(neat.StdOutReporter(True))
    population.add_reporter(neat.StatisticsReporter())

    # Run neuroevolution for a fixed number of generations
    # signature: run(fitness_function, n_generations) -> best_genome
    # NEAT calls eval_genomes for each generation
    winner = population.run(eval_genomes, GENERATIONS)

    print("\nBest genome found:\n", winner)

    with open("best_robot.pkl", "wb") as f:
        pickle.dump(winner, f)


    # Test best controller against random opponents
    winner_net = neat.nn.FeedForwardNetwork.create(winner, config)
    print("\nTesting best genome against random opponents")

    for _ in range(5):
        opponent_genome = random.choice(list(population.population.values()))
        opponent_net = neat.nn.FeedForwardNetwork.create(opponent_genome, config)

        f1, f2 = simulate_battle(winner_net, opponent_net)
        print(f"Winner fitness: {f1:.2f}, Opponent fitness: {f2:.2f}")


if __name__ == "__main__":
    main()
