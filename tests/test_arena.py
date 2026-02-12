import unittest
from unittest.mock import MagicMock
import math
import sys
import os

# Add parent directory to path to allow importing modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from arena import Arena
from robot import Robot

class TestArena(unittest.TestCase):
    def setUp(self):
        self.mock_controller = MagicMock()
        self.mock_controller.activate.return_value = (0, 0, 0) # Default no-op action
        
        self.robot1 = Robot(self.mock_controller, start_pos=(0.2, 0.5))
        self.robot2 = Robot(self.mock_controller, start_pos=(0.8, 0.5))
        self.arena = Arena(width=1.0, height=1.0, robots=[self.robot1, self.robot2], max_steps=100)

    def test_initialization(self):
        self.assertEqual(self.arena.width, 1.0)
        self.assertEqual(self.arena.height, 1.0)
        self.assertEqual(len(self.arena.robots), 2)
        self.assertEqual(self.arena.max_steps, 100)
        self.assertEqual(self.arena.current_step, 0)

    def test_keep_inside(self):
        # Move robot outside
        self.robot1.x = -0.1
        self.robot1.y = 1.2
        
        self.arena.keep_inside(self.robot1)
        
        self.assertEqual(self.robot1.x, 0)
        self.assertEqual(self.robot1.y, 1.0)

    def test_step_increases_counter(self):
        self.arena.step()
        self.assertEqual(self.arena.current_step, 1)

    def test_is_done_max_steps(self):
        self.arena.current_step = 100
        self.assertTrue(self.arena.is_done())

    def test_is_done_robot_dead(self):
        self.robot1.health = 0
        self.assertTrue(self.arena.is_done())

    def test_shoot_hit(self):
        # Position robots so robot1 hits robot2
        # robot1 at (0.2, 0.5), facing 0 (right)
        # robot2 at (0.3, 0.5) -> dx=0.1, dy=0, dist=0.1, angle=0
        
        self.robot1.x = 0.2
        self.robot1.y = 0.5
        self.robot1.angle = 0.0
        
        self.robot2.x = 0.3
        self.robot2.y = 0.5
        
        # Action to shoot: (move, rotate, shoot)
        # shoot > 0.5
        self.robot1.last_action = (0, 0, 1.0)
        
        initial_health = self.robot2.health
        self.arena.apply_damage()
        
        self.assertEqual(self.robot2.health, initial_health - self.arena.DAMAGE)
        self.assertEqual(self.robot1.damage_inflicted, self.arena.DAMAGE)

    def test_shoot_miss_range(self):
        # Too far
        self.robot2.x = 0.2 + self.arena.SHOOT_RANGE + 0.1
        self.robot1.last_action = (0, 0, 1.0)
        
        initial_health = self.robot2.health
        self.arena.apply_damage()
        
        self.assertEqual(self.robot2.health, initial_health)

    def test_shoot_miss_angle(self):
        # Wrong angle
        self.robot1.angle = math.pi # Facing left
        self.robot2.x = 0.3 # To the right
        
        self.robot1.last_action = (0, 0, 1.0)
        
        initial_health = self.robot2.health
        self.arena.apply_damage()
        
        self.assertEqual(self.robot2.health, initial_health)

    def test_normalize_angle(self):
        self.assertAlmostEqual(self.arena.normalize_angle(math.pi + 0.1), -math.pi + 0.1)
        self.assertAlmostEqual(self.arena.normalize_angle(-math.pi - 0.1), math.pi - 0.1)
        self.assertAlmostEqual(self.arena.normalize_angle(0), 0)

if __name__ == '__main__':
    unittest.main()
