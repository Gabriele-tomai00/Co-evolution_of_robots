import unittest
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from controllers import RandomController, StaticShooter, AggressiveChaser

class TestControllers(unittest.TestCase):
    def test_random_controller(self):
        controller = RandomController()
        steering, throttle, shoot = controller.act()
        
        self.assertTrue(-1 <= steering <= 1)
        self.assertTrue(0 <= throttle <= 1)
        self.assertIn(shoot, [True, False])

    def test_static_shooter(self):
        controller = StaticShooter()
        # sensors: [distance, angle_diff, ...] - we only care about angle_diff at index 1
        # Test aiming left (positive angle diff)
        sensors = [0.5, 0.1, 0, 0, 0] 
        steering, throttle, shoot = controller.act(sensors)
        
        self.assertGreater(steering, 0) # Should steer right/positive to correct? Or matches angle?
        # Code: steering = angle_diff * 5.0
        # If angle_diff is positive, steering is positive.
        self.assertEqual(throttle, 0.0)
        self.assertTrue(shoot)

    def test_aggressive_chaser(self):
        controller = AggressiveChaser()
        
        # Test aligned
        sensors_aligned = [0.5, 0.0, 0, 0, 0]
        steering, throttle, shoot = controller.act(sensors_aligned)
        
        self.assertEqual(steering, 0.0)
        self.assertEqual(throttle, 1.0)
        self.assertTrue(shoot) # abs(0) < 0.2 -> True

        # Test misaligned
        sensors_misaligned = [0.5, 0.5, 0, 0, 0]
        steering, throttle, shoot = controller.act(sensors_misaligned)
        
        self.assertGreater(steering, 0)
        self.assertEqual(throttle, 1.0)
        self.assertFalse(shoot) # abs(0.5) > 0.2 -> False

if __name__ == '__main__':
    unittest.main()
