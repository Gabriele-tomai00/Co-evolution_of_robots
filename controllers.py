#    Gabriele Tomai
#    Student ID: IN2300006
#    Degree Program: Computer Engineering

import random

# Responsabilità
# Implementa la policy decisionale del robot.
#
# Compiti principali
#
# Riceve i valori dei sensori
#
# Produce azioni di controllo (movimento, rotazione, attacco)
#
# Incapsula il modello evolvibile (NEAT, GP, ecc.)
#
# Nota concettuale
# È l’unica parte che viene evoluta.
# Tutto il resto del sistema rimane fisso.

class RandomController:
    def act(self, sensors):
        steering = random.uniform(-1, 1)
        throttle = random.uniform(0, 1)
        shoot = random.random() < 0.1
        return steering, throttle, shoot
