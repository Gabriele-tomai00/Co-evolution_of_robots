#    Gabriele Tomai
#    Student ID: IN2300006
#    Degree Program: Computer Engineering

import argparse
import neat
import random
import pickle
import time
import datetime
import sys
from utils import print_ascii_logo, eval_genomes, test_best_genome_against_random_opponents, print_summary
GENERATIONS = 15

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
    print(f"Population size: {config.pop_size}")

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
    
    # Retrieve custom fitness components if available
    fit_int = getattr(winner, "fitness_internal", 0.0)
    fit_ext = getattr(winner, "fitness_external", 0.0)
    
    # Approximate averages based on config (assuming standard run)
    # pop_size is in config.pop_size
    # External matches is 6 (fixed in utils.py)
    # Internal matches is pop_size - 1
    pop_size = config.pop_size
    avg_int = fit_int / (pop_size - 1) if pop_size > 1 else 0.0
    avg_ext = fit_ext / 6.0
    
    print(f"Best Genome ID: {winner.key}")
    print(f"Total Fitness: {winner.fitness:.2f}")
    print(f" - Internal Fitness (vs population): {avg_int:.2f} (raw: {fit_int:.1f})")
    print(f" - External Fitness (vs opponents):  {avg_ext:.2f} (raw: {fit_ext:.1f})")
    
    num_nodes = len(winner.nodes)
    num_connections = sum(1 for c in winner.connections.values() if c.enabled)
    print(f"Network Complexity: {num_nodes} nodes, {num_connections} connections")

    if verbose:
        print("\nRaw NEAT genome (including nodes and connections):\n")
        print(winner)

    with open("best_robot.pkl", "wb") as f:
        pickle.dump(winner, f)

    # Test best controller against random opponents
    winner_net = neat.nn.FeedForwardNetwork.create(winner, config)
    print("\n=== PHASE 3: Testing best genome against random opponents ===")

    results = test_best_genome_against_random_opponents(winner_net)

    crushing_threshold = 50.0

    total_matches = len(results)
    wins = 0
    crushing_wins = 0
    draws = 0
    losses = 0
    crushing_losses = 0

    for _, _, f1, f2, _ in results:
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

    print(f"Matches: {total_matches}")
    print(f"Wins: {wins + crushing_wins} ({wins} normal, {crushing_wins} crushing)")
    print(f"Draws: {draws}")
    print(f"Losses: {losses + crushing_losses}")
    print(f"Win Rate: {win_rate * 100:.1f}%")

    # SUMMARIZE EXECUTION
    end_time = time.time()
    duration_seconds = int(end_time - start_time)
    minutes, seconds = divmod(duration_seconds, 60)
    start_time_str = datetime.datetime.fromtimestamp(start_time).strftime("%H:%M:%S")
    end_time_str = datetime.datetime.now().strftime("%H:%M:%S")
    duration_str = f"{minutes}m {seconds}s"

    print_summary(start_time_str, end_time_str, duration_str, win_rate)

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

    try:
        main(verbose=args.verbose, generations=args.generations, pop_size=args.pop_size)
        
    except (KeyboardInterrupt, EOFError):
        print("\nExecution interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"An error occurred: {e}")
