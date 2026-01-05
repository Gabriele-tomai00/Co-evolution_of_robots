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

@dataclass
class Robot:
    x: float
    y: float
    angle: float
    energy: float = 100.0
    alive: bool = True

    radius: float = 0.5
    max_speed: float = 1.0
    turn_speed: float = math.pi / 8

    def move(self, throttle: float, steering: float, arena_size: int):
        if not self.alive:
            return

        self.angle += steering * self.turn_speed
        dx = math.cos(self.angle) * throttle * self.max_speed
        dy = math.sin(self.angle) * throttle * self.max_speed

        self.x = min(max(self.x + dx, 0), arena_size)
        self.y = min(max(self.y + dy, 0), arena_size)

    def take_damage(self, amount: float):
        self.energy -= amount
        if self.energy <= 0:
            self.alive = False
