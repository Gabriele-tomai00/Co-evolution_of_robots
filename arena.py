import math
from sensors import compute_sensors

# Responsabilità
# Simula l’ambiente e le regole dell’interazione tra robot.
#
# Compiti principali
#
# Gestisce il ciclo temporale della simulazione
#
# Applica le azioni dei robot a ogni step
#
# Valuta collisioni, limiti dell’arena e combattimento
#
# Determina la fine di un match e il vincitore
#
# Nota concettuale
# L’arena è deterministica e neutrale: non favorisce nessuna strategia.

class Arena:
    def __init__(self, size=20, max_steps=500):
        self.size = size
        self.max_steps = max_steps

    def step(self, robot_a, robot_b, ctrl_a, ctrl_b):
        sensors_a = compute_sensors(robot_a, robot_b, self.size)
        sensors_b = compute_sensors(robot_b, robot_a, self.size)

        steer_a, throttle_a, shoot_a = ctrl_a.act(sensors_a)
        steer_b, throttle_b, shoot_b = ctrl_b.act(sensors_b)

        robot_a.move(throttle_a, steer_a, self.size)
        robot_b.move(throttle_b, steer_b, self.size)

        self._handle_shooting(robot_a, robot_b, shoot_a)
        self._handle_shooting(robot_b, robot_a, shoot_b)

    def _handle_shooting(self, attacker, target, shoot):
        if not shoot or not attacker.alive or not target.alive:
            return

        dx = target.x - attacker.x
        dy = target.y - attacker.y
        distance = math.hypot(dx, dy)

        if distance < 5.0:
            target.take_damage(10.0)

    def run_match(self, robot_a, robot_b, ctrl_a, ctrl_b):
        for step in range(self.max_steps):
            if not robot_a.alive or not robot_b.alive:
                break
            self.step(robot_a, robot_b, ctrl_a, ctrl_b)

        return self._winner(robot_a, robot_b)

    @staticmethod
    def _winner(robot_a, robot_b):
        if robot_a.alive and not robot_b.alive:
            return 1
        if robot_b.alive and not robot_a.alive:
            return -1
        return 0
