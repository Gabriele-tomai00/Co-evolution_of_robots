#    Gabriele Tomai
#    Student ID: IN2300006
#    Degree Program: Computer Engineering

import random

class RandomController:
    def act(self, sensors):
        steering = random.uniform(-1, 1)
        throttle = random.uniform(0, 1)
        shoot = random.random() < 0.1
        return steering, throttle, shoot


class StaticShooter:
    """
    A stationary robot that rotates to face the opponent and shoots constantly.
    Tests the opponent's ability to dodge or attack quickly.
    """
    def act(self, sensors):
        # sensors[1] is angle_diff (normalized [-1, 1])
        # If angle_diff > 0, enemy is to the left/right? 
        # Actually sensors[1] is (angle_to_opponent - my_angle)
        # We want to minimize this difference.
        
        angle_diff = sensors[1]
        
        # Simple P-controller for steering
        steering = angle_diff * 5.0 
        steering = max(-1.0, min(1.0, steering))
        
        throttle = 0.0  # Stay still
        shoot = True    # Always shoot
        
        return steering, throttle, shoot


class AggressiveChaser:
    """
    A robot that moves directly towards the opponent and shoots.
    Tests the opponent's ability to kite or overpower in close combat.
    """
    def act(self, sensors):
        angle_diff = sensors[1]
        distance = sensors[0]
        
        # Steer towards opponent
        steering = angle_diff * 5.0
        steering = max(-1.0, min(1.0, steering))
        
        # Always move forward
        throttle = 1.0
        
        # Shoot if relatively aligned
        shoot = abs(angle_diff) < 0.2
        
        return steering, throttle, shoot
