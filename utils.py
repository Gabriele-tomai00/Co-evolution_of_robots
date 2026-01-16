#    Gabriele Tomai
#    Student ID: IN2300006
#    Degree Program: Computer Engineering

import random
import neat

from arena import Arena
from robot import Robot
from sensors import Sensors

# Maximum number of simulation steps for a single battle
MAX_STEPS = 300

def print_ascii_logo():
    ascii_art = r"""
  ____                            _       _   _                      __ 
 / ___|___         _____   _____ | |_   _| |_(_) ___  _ __     ___  / _|
| |   / _ \ _____ / _ \ \ / / _ \| | | | | __| |/ _ \| '_ \   / _ \| |_ 
| |__| (_) |_____|  __/\ V / (_) | | |_| | |_| | (_) | | | | | (_) |  _|
 \____\___/ _     \___| \_/ \___/|_|\__,_|\__|_|\___/|_| |_|  \___/|_|  
|  _ \ ___ | |__   ___ | |_ ___                                         
| |_) / _ \| '_ \ / _ \| __/ __|                                        
|  _ < (_) | |_) | (_) | |_\__ \                                        
|_| \_\___/|_.__/ \___/ \__|___/                                         
"""
    print(ascii_art)


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

    


# Number of generations for the evolutionary process
GENERATIONS = 15


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
    


def test_best_genome_against_random_opponents(winner_net, population, config, num_tests=100):
    """
    Test the best genome against random opponents from the current population.

    Args:
        winner_net: the neural network of the best genome
        population: a dict of all genomes in the population
        config: NEAT config
        num_tests: number of random opponents to test against

    Returns:
        results: list of [match_number, who_won, winner_fitness, opponent_fitness]
    """

    results = []
    for i in range(num_tests):
        opponent_genome = random.choice(list(population.population.values()))
        opponent_net = neat.nn.FeedForwardNetwork.create(opponent_genome, config)

        f1, f2 = simulate_battle(winner_net, opponent_net)

        # Decide who "won" the match for display
        winner_label = "Winner" if f1 >= f2 else "Opponent"

        # Add to results list
        results.append([i+1, winner_label, f1, f2])
    return results

