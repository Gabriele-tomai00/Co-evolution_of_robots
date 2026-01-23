#    Gabriele Tomai
#    Student ID: IN2300006
#    Degree Program: Computer Engineering

import random
import neat
import os
from controllers import RandomController, StaticShooter, AggressiveChaser
from arena import Arena
from robot import Robot
from sensors import Sensors

# Maximum number of simulation steps for a single battle
MAX_STEPS = 300
filename_for_fitness_history = "fitness_history.csv"

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


# Wrappers for new controllers to match .activate() interface
class RandomWrapper:
    def __init__(self):
        self.controller = RandomController()
    def activate(self, _):
        return self.controller.act()

class StaticWrapper:
    def __init__(self):
        self.controller = StaticShooter()
    def activate(self, sensors):
        return self.controller.act(sensors)

class ChaserWrapper:
    def __init__(self):
        self.controller = AggressiveChaser()
    def activate(self, sensors):
        return self.controller.act(sensors)

# Worker function for round-robin battles
def worker_battle(args):
    id1, net1, id2, net2 = args
    f1, f2 = simulate_battle(net1, net2)
    return id1, f1, id2, f2

# Worker function for random battles
def worker_random_battle(args):
    genome_id, net = args
    # We need to recreate RandomWrapper here to ensure new random state/opponent
    opponent = RandomWrapper()
    f_genome, _ = simulate_battle(net, opponent)
    return genome_id, f_genome


# Global generation counter for logging
generation_count = 0

def eval_genomes(genomes, config):
    """
    Evaluation function required by neat-python.
    Each genome is evaluated by fighting against other genomes.
    """
    global generation_count

    # Initialize fitness for all genomes
    for _, genome in genomes:
        genome.fitness = 0.0
        # Custom attributes for tracking internal vs external performance
        genome.fitness_internal = 0.0
        genome.fitness_external = 0.0

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
            genomes[i][1].fitness_internal += f1
            genomes[j][1].fitness_internal += f2
    
    # Validation against multiple opponents to prevent overfitting
    # Each genome plays against Random, Static, and Chaser bots
    for genome_id, genome in genomes:
        net = networks[genome_id]
        
        # 1. Fight against Random (unpredictable) - 2 matches
        for _ in range(2):
            opponent = RandomWrapper()
            f_genome, _ = simulate_battle(net, opponent)
            genome.fitness_external += f_genome
            
        # 2. Fight against Static (aim test) - 2 matches
        for _ in range(4):
            opponent = StaticWrapper()
            f_genome, _ = simulate_battle(net, opponent)
            genome.fitness_external += f_genome
        
        # 3. Fight against Chaser (pressure test) - 2 matches
        for _ in range(4):
            opponent = ChaserWrapper()
            f_genome, _ = simulate_battle(net, opponent)
            genome.fitness_external += f_genome
            
    # Combine fitness and calculate stats
    total_internal = 0.0
    total_external = 0.0
    
    # Calculate number of matches
    num_opponents = len(genome_ids) - 1
    num_external_matches = 6 # 2 Random + 2 Static + 2 Chaser
    
    for _, genome in genomes:
        # Normalize fitness by number of matches to balance incentives
        avg_internal_score = genome.fitness_internal / num_opponents if num_opponents > 0 else 0.0
        avg_external_score = genome.fitness_external / num_external_matches
        
        # Total fitness determines selection
        # We give equal weight to internal (co-evolution) and external (robustness) performance
        genome.fitness = avg_internal_score + avg_external_score
        
        # For stats, we keep tracking the raw totals or averages? 
        # Let's track averages to make them comparable in the CSV
        total_internal += avg_internal_score
        total_external += avg_external_score

    # Calculate population averages of the per-match scores
    avg_internal_pop = total_internal / len(genomes)
    avg_external_pop = total_external / len(genomes)
    
    print(f" > [Gen {generation_count}] Avg Score/Match - Internal: {avg_internal_pop:.2f} | External: {avg_external_pop:.2f}")
    log_fitness_history(generation_count, avg_internal_pop, avg_external_pop)
    
    generation_count += 1

def log_fitness_history(gen, avg_int, avg_ext):
    """
    Appends fitness statistics to a CSV file.
    """
    if not os.path.exists(filename_for_fitness_history) or gen == 0:
        with open(filename_for_fitness_history, "w") as f:
            f.write("Generation,Avg_Internal_Score_Per_Match,Avg_External_Score_Per_Match\n")
            
    with open(filename_for_fitness_history, "a") as f:
        f.write(f"{gen},{avg_int:.2f},{avg_ext:.2f}\n")
    
def test_best_genome_against_random_opponents(winner_net, num_tests=100):
    """
    Test the best genome against a mix of opponents:
    1. RandomController (unpredictable)
    2. StaticShooter (perfect aim, stationary)
    3. AggressiveChaser (perfect aim, chases)
    
    Returns:
        results: list of [match_number, who_won, winner_fitness, opponent_fitness, opponent_type]
    """

    results = []
    
    # Split tests to match training distribution (approx 20% Random, 40% Static, 40% Chaser)
    num_random = int(num_tests * 0.2)
    num_static = int(num_tests * 0.4)
    num_chaser = num_tests - num_random - num_static
    
    opponents = []
    for _ in range(num_random): opponents.append(("Random", RandomWrapper()))
    for _ in range(num_static): opponents.append(("Static", StaticWrapper()))
    for _ in range(num_chaser): opponents.append(("Chaser", ChaserWrapper()))
    
    random.shuffle(opponents)

    for i, (opp_type, opponent_net) in enumerate(opponents):
        f1, f2 = simulate_battle(winner_net, opponent_net)

        # Decide who "won" the match for display
        winner_label = "Winner" if f1 >= f2 else opp_type

        # Add to results list
        results.append([i+1, winner_label, f1, f2, opp_type])
    return results


def print_summary(start_time_str, end_time_str, duration_str, win_rate):
    """
    Print a summary of the execution to the console.
    """
        
    print("\n====== Summary =======")
    print(f"Start time: {start_time_str}")
    print(f"End time: {end_time_str}")
    print(f"Duration: {duration_str}")
    print(f"Win rate: {win_rate * 100:.1f}%")
    print("=====================")
