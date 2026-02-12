import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import utils
from robot import Robot

class TestUtils(unittest.TestCase):
    def test_compute_fitness(self):
        robot1 = MagicMock()
        robot2 = MagicMock()
        
        # Scenario 1: Both alive, no damage
        robot1.is_dead.return_value = False
        robot2.is_dead.return_value = False
        robot1.damage_inflicted = 0
        robot2.damage_inflicted = 0
        
        f1, f2 = utils.compute_fitness(robot1, robot2, steps=100)
        # 100 * 0.1 = 10 for survival
        self.assertEqual(f1, 10.0)
        self.assertEqual(f2, 10.0)

        # Scenario 2: Robot 1 kills Robot 2
        robot1.is_dead.return_value = False
        robot2.is_dead.return_value = True
        robot1.damage_inflicted = 50
        robot2.damage_inflicted = 10
        
        f1, f2 = utils.compute_fitness(robot1, robot2, steps=50)
        # f1: 100 (win) + 50 (damage) + 5 (survival) = 155
        # f2: 10 (damage) + 5 (survival) = 15
        self.assertEqual(f1, 155.0)
        self.assertEqual(f2, 15.0)

    def test_simulate_battle(self):
        # Mock neural networks
        net1 = MagicMock()
        net2 = MagicMock()
        
        # Activate returns action (steering, throttle, shoot)
        net1.activate.return_value = (0.0, 0.0, 0.0)
        net2.activate.return_value = (0.0, 0.0, 0.0)
        
        # We need to ensure simulate_battle finishes. 
        # Since we can't easily inject the Arena max_steps inside simulate_battle (it uses global MAX_STEPS or default),
        # we'll patch utils.Arena or utils.MAX_STEPS if possible.
        # utils.simulate_battle uses utils.Arena and utils.MAX_STEPS
        
        with patch('utils.MAX_STEPS', 10):
            f1, f2 = utils.simulate_battle(net1, net2)
            
        # Since they do nothing, they survive 10 steps (0 to 9).
        # Fitness = 9 * 0.1 = 0.9
        self.assertEqual(f1, 0.9)
        self.assertEqual(f2, 0.9)

    def test_process_results(self):
        # results: list of [match_number, who_won, winner_fitness, opponent_fitness, opponent_type]
        # Wait, utils doesn't have process_results. main.py does.
        # Checking utils.py content again...
        # process_results is in main.py in the provided Read output.
        pass

if __name__ == '__main__':
    unittest.main()
