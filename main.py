import argparse
import neat
import random
import pickle
from tabulate import tabulate

from utils import *


def main(verbose: bool = False):
    print_ascii_logo()
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

    print("\n=== PHASE 1: Evolving robots with NEAT ===")
    print(f"Generations: {GENERATIONS}")

    # Report evolution progress and statistics
    if verbose:
        population.add_reporter(neat.StdOutReporter(True))
    else:
        population.add_reporter(neat.StdOutReporter(False))
    population.add_reporter(neat.StatisticsReporter())

    # Run neuroevolution for a fixed number of generations
    # signature: run(fitness_function, n_generations) -> best_genome
    # NEAT calls eval_genomes for each generation
    winner = population.run(eval_genomes, GENERATIONS)

    print("\n=== PHASE 2: Best genome found ===")
    num_nodes = len(winner.nodes)
    num_connections = sum(1 for c in winner.connections.values() if c.enabled)

    best_summary = [[
        getattr(winner, "key", "N/A"),
        f"{getattr(winner, 'fitness', 0.0):.2f}",
        num_nodes,
        num_connections,
    ]]

    print(
        tabulate(
            best_summary,
            headers=["Genome ID", "Fitness", "Nodes", "Enabled connections"],
            tablefmt="grid",
        )
    )

    if verbose:
        print("\nRaw NEAT genome (including nodes and connections):\n")
        print(winner)

    with open("best_robot.pkl", "wb") as f:
        pickle.dump(winner, f)


    # Test best controller against random opponents
    winner_net = neat.nn.FeedForwardNetwork.create(winner, config)
    print("\n=== PHASE 3: Testing best genome against random opponents ===")

    results = test_best_genome_against_random_opponents(winner_net, population, config)

    # Print as ASCII table
    print(
        tabulate(
            results,
            headers=["Match", "Who Won", "Winner Fitness", "Opponent Fitness"],
            tablefmt="grid",
            floatfmt=".2f",
        )
    )

    num_matches = len(results)
    num_wins = sum(1 for _, who_won, _, _ in results if who_won == "Winner")
    num_losses = num_matches - num_wins
    print(f"\nSummary: {num_wins}/{num_matches} wins, {num_losses} losses.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Co-evolution of robots with NEAT"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print detailed NEAT evolution logs",
    )
    args = parser.parse_args()
    main(verbose=args.verbose)
