import unittest
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import main

class TestMain(unittest.TestCase):
    def test_process_results(self):
        # process_results(results, crushing_threshold=50.0)
        # results format: [match_num, winner_label, f1, f2, opp_type]
        
        results = [
            [1, "Winner", 100.0, 90.0, "Random"],   # Win (diff 10 < 50)
            [2, "Winner", 150.0, 50.0, "Random"],   # Crushing Win (diff 100 >= 50)
            [3, "Winner", 100.0, 100.0, "Static"],  # Draw (diff 0 < 1)
            [4, "Chaser", 50.0, 60.0, "Chaser"],    # Loss (diff -10 > -50)
            [5, "Chaser", 10.0, 100.0, "Chaser"],   # Crushing Loss (diff -90 <= -50)
        ]
        
        wins, crushing_wins, draws, losses, crushing_losses = main.process_results(results, crushing_threshold=50.0)
        
        self.assertEqual(wins, 1)
        self.assertEqual(crushing_wins, 1)
        self.assertEqual(draws, 1)
        self.assertEqual(losses, 1)
        self.assertEqual(crushing_losses, 1)

if __name__ == '__main__':
    unittest.main()
