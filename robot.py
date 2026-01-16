#    Gabriele Tomai
#    Student ID: IN2300006
#    Degree Program: Computer Engineering

from dataclasses import dataclass
import math

# Responsabilità
    # Rappresenta l’agente fisico all’interno dell’arena.
# Compiti principali
    # Mantiene lo stato del robot (posizione, orientamento, energia, vita)
    # Applica le azioni ricevute dal controller (movimento, rotazione)
    # Gestisce i danni e la condizione di morte
# Nota concettuale
    # Il robot non prende decisioni: esegue soltanto.
    # Questo separa nettamente il modello fisico dalla policy di controllo.

class Robot:
    def __init__(self, controller, start_pos=(0.0, 0.0)):
        self.controller = controller
        self.x, self.y = start_pos
        self.angle = 0.0           # facing right
        self.max_health = 100
        self.health = self.max_health
        self.damage_inflicted = 0
        self.last_action = (0.0, 0.0, 0.0)

    def apply_action(self, action):
        # Action[0] = move: -1 backward, 1 forward
        move = action[0] * 1.0
        self.x += math.cos(self.angle) * move
        self.y += math.sin(self.angle) * move

        # Action[1] = rotate: -1 left, 1 right
        rotate = action[1] * 0.1
        self.angle += rotate

        # Action[2] = shoot: 0 = nothing, >0 = shoot
        if action[2] > 0.5:
            self.shoot()

        # Store last action for environment processing (damage, etc.)
        self.last_action = action

    def shoot(self):
        # minimal logic: damage will be applied in Arena
        pass

    def is_dead(self):
        return self.health <= 0
