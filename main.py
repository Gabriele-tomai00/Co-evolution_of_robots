#    Gabriele Tomai
#    Student ID: IN2300006
#    Degree Program: Computer Engineering

import argparse
import neat
import random
import pickle
import time
import datetime
from tabulate import tabulate

from utils import *
# Number of generations for the evolutionary process
GENERATIONS = 15
log_file = "execution_log.txt"


def main(verbose: bool = False, generations: int = None, pop_size: int = None):
    start_time = time.time()
    start_time_str = datetime.datetime.now().strftime("%H:%M:%S")
    print_ascii_logo()
    # Set random seed for reproducibility, used in genome evaluation
    # when the other istances use the same seed, the genomes will be the same
    random.seed(0)

    # Load NEAT configuration (same structure as course notebook)
    config = neat.Config(
        neat.genome.DefaultGenome,
        neat.reproduction.DefaultReproduction,
        neat.species.DefaultSpeciesSet,
        neat.stagnation.DefaultStagnation,
        "neat_config.txt"
    )

    # Override configuration if arguments are provided
    if pop_size is not None:
        config.pop_size = pop_size
        print(f"Overriding population size to: {pop_size}")

    # Initialize population of neural networks
    population = neat.Population(config)

    # Determine number of generations
    n_generations = generations if generations is not None else GENERATIONS

    print("\n=== PHASE 1: Evolving robots with NEAT ===")
    print(f"Generations: {n_generations}")

    # Report evolution progress and statistics
    if verbose:
        population.add_reporter(neat.StdOutReporter(True))
    else:
        population.add_reporter(neat.StdOutReporter(False))
    population.add_reporter(neat.StatisticsReporter())

    # Run neuroevolution for a fixed number of generations
    # signature: run(fitness_function, n_generations) -> best_genome
    # NEAT calls eval_genomes for each generation
    winner = population.run(eval_genomes, n_generations)

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

    detailed_results = results[:3]
    print("\nFirst 3 matches:")
    print(
        tabulate(
            detailed_results,
            headers=["Match", "Who Won", "Winner Fitness", "Opponent Fitness"],
            tablefmt="grid",
            floatfmt=".2f",
        )
    )

    if len(results) > len(detailed_results):
        print("...")

    crushing_threshold = 50.0

    total_matches = len(results)
    wins = 0
    crushing_wins = 0
    draws = 0
    losses = 0
    crushing_losses = 0

    for _, _, f1, f2 in results:
        diff = f1 - f2
        if abs(diff) < 1.0:
            draws += 1
        elif diff > 0:
            if diff >= crushing_threshold:
                crushing_wins += 1
            else:
                wins += 1
        else:
            if -diff >= crushing_threshold:
                crushing_losses += 1
            else:
                losses += 1

    effective_wins = wins + crushing_wins
    win_rate = (effective_wins / total_matches) if total_matches > 0 else 0.0

    summary_table = [[
        total_matches,
        wins,
        crushing_wins,
        draws,
        losses,
        crushing_losses,
        f"{win_rate * 100:.1f}%",
    ]]
    print("Summary of matches:")
    print(
        tabulate(
            summary_table,
            headers=[
                "Total",
                "Wins",
                "Crushing wins",
                "Draws",
                "Losses",
                "Crushing losses",
                "Win rate",
            ],
            tablefmt="grid",
        )
    )

    print(
        "\nDefinitions:\n"
        f"- Crushing win: winner's fitness at least {crushing_threshold} points higher than opponent.\n"
        f"- Crushing loss: winner's fitness at least {crushing_threshold} points lower than opponent.\n"
        "- Draw: absolute fitness difference less than 1.0."
    )

    # SUMMARIZE EXECUTION
    end_time = time.time()
    duration_seconds = int(end_time - start_time)
    minutes, seconds = divmod(duration_seconds, 60)
    start_time_str = datetime.datetime.fromtimestamp(start_time).strftime("%H:%M:%S")
    end_time_str = datetime.datetime.now().strftime("%H:%M:%S")
    duration_str = f"{minutes}m {seconds}s"

    print_summary(start_time_str, end_time_str, duration_str, win_rate)
    # Save summary to log file
    save_execution_log(log_file, n_generations, config.pop_size, winner.fitness, win_rate, duration_str)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Co-evolution of robots with NEAT"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print detailed NEAT evolution logs",
    )
    parser.add_argument(
        "--generations",
        type=int,
        help="Number of generations to run evolution",
    )
    parser.add_argument(
        "--pop-size",
        type=int,
        help="Population size (overrides config file)",
    )
    args = parser.parse_args()
    main(verbose=args.verbose, generations=args.generations, pop_size=args.pop_size)
