#    Gabriele Tomai
#    Student ID: IN2300006
#    Degree Program: Computer Engineering

import math


class Sensors:
    """
    Sensors are responsible for extracting a partial, numerical observation
    of the environment for a given robot.
    This observation will be fed directly to the neural network.
    """

    @staticmethod
    def get(robot, arena):
        """
        Compute the sensor vector for a robot inside the arena.
        Returns a list of floats with fixed size and ordering.
        """

        opponent = Sensors._get_opponent(robot, arena)
        # Relative position to opponent
        dx = opponent.x - robot.x
        dy = opponent.y - robot.y
        distance = math.hypot(dx, dy)

        # Angle difference between robot orientation and opponent direction
        angle_to_opponent = math.atan2(dy, dx)
        angle_diff = Sensors._normalize_angle(angle_to_opponent - robot.angle)

        # Distances from arena walls (normalized)
        # We provide 4 separate distances (left, right, bottom, top) instead of just (x, y) coordinates.
        # This explicit representation makes it easier for the neural network to detect proximity to boundaries
        # and learn to avoid collisions without performing complex internal calculations.
        dist_left = robot.x
        dist_right = arena.width - robot.x
        dist_bottom = robot.y
        dist_top = arena.height - robot.y

        # Normalize values to reasonable ranges
        max_dist = math.hypot(arena.width, arena.height)
        # normalized
        sensors = [
            distance / max_dist,
            angle_diff / math.pi,
            robot.health / robot.max_health,
            dist_left / arena.width,
            dist_right / arena.width,
            dist_bottom / arena.height,
            dist_top / arena.height
        ]

        return sensors

    @staticmethod
    def _get_opponent(robot, arena):
        """
        Return the opponent robot in a 1v1 arena.
        """
        for r in arena.robots:
            if r is not robot:
                return r
        raise ValueError("Opponent not found in arena")

    @staticmethod
    def _normalize_angle(angle):
        """
        Normalize angle to the range [-pi, pi].
        """
        while angle > math.pi:
            angle -= 2 * math.pi
        while angle < -math.pi:
            angle += 2 * math.pi
        return angle
