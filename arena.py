#    Gabriele Tomai
#    Student ID: IN2300006
#    Degree Program: Computer Engineering

import math

class Arena:
    def __init__(self, width=1.0, height=1.0, robots=None, max_steps=1000):
        self.width = width
        self.height = height
        self.robots = robots or []
        self.max_steps = max_steps
        self.current_step = 0
        self.DAMAGE = 10  # health points per hit
        self.SHOOT_RANGE = 0.2  # max distance for conditional hit
        self.SHOOT_ANGLE = math.radians(30)  # max angle difference for conditional hit

    def step(self):
        self.current_step += 1
        for robot in self.robots:
            sensors = self.get_sensors(robot)
            action = robot.controller.activate(sensors)
            robot.apply_action(action)

        # After all robots moved, apply damage if they shot
        self.apply_damage()

        # Keep robots inside arena
        for robot in self.robots:
            self.keep_inside(robot)

    def apply_damage(self):
        """
        Apply damage when a robot shoots and the target is within range and angle.
        Uses the robot's last_action to determine if a shot was fired.
        """
        for shooter in self.robots:
            last_action = getattr(shooter, "last_action", None)
            if last_action is None:
                continue
            if last_action[2] > 0.5:
                for target in self.robots:
                    if target == shooter:
                        continue
                    dx = target.x - shooter.x
                    dy = target.y - shooter.y
                    distance = math.hypot(dx, dy)
                    angle_to_target = math.atan2(dy, dx)
                    angle_diff = abs(self.normalize_angle(shooter.angle - angle_to_target))
                    if distance <= self.SHOOT_RANGE and angle_diff <= self.SHOOT_ANGLE:
                        target.health -= self.DAMAGE
                        shooter.damage_inflicted += self.DAMAGE

    def normalize_angle(self, angle):
        # normalize angle to [-pi, pi]
        while angle > math.pi:
            angle -= 2*math.pi
        while angle < -math.pi:
            angle += 2*math.pi
        return angle

    def keep_inside(self, robot):
        robot.x = max(0, min(robot.x, self.width))
        robot.y = max(0, min(robot.y, self.height))

    def is_done(self):
        if self.current_step >= self.max_steps:
            return True
        for robot in self.robots:
            if robot.is_dead():
                return True
        return False

    # for the NEAT evaluation
    def get_sensors(self, robot):
        # minimal example: distance and angle to opponent
        opponent = next(r for r in self.robots if r != robot)
        dx = opponent.x - robot.x
        dy = opponent.y - robot.y
        distance = math.hypot(dx, dy)
        angle_to_opponent = math.atan2(dy, dx)
        angle_diff = self.normalize_angle(robot.angle - angle_to_opponent)
        return [distance, angle_diff, robot.health / 100.0]  # normalized health