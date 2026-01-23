#    Gabriele Tomai
#    Student ID: IN2300006
#    Degree Program: Computer Engineering

import math

class Arena:
    """
    Manages the battle simulation, including robots, basic physics,
    and engagement rules.
    """
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
        """
        Executes a single simulation step: updates sensors,
        applies robot actions, and calculates damage.
        """
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
            self._process_shooter_shot(shooter)

    def _process_shooter_shot(self, shooter):
        last_action = getattr(shooter, "last_action", None)
        if last_action is None or last_action[2] <= 0.5:
            return

        for target in self.robots:
            if target != shooter:
                self._check_and_apply_hit(shooter, target)

    def _check_and_apply_hit(self, shooter, target):
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
        """
        Checks if the battle is over due to maximum steps reached
        or if one robot is dead.
        """
        if self.current_step >= self.max_steps:
            return True
        for robot in self.robots:
            if robot.is_dead():
                return True
        return False