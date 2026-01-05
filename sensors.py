import math

# Responsabilità
# Trasforma lo stato globale della simulazione in input locali per il controller.
#
# Compiti principali
#
# Calcola informazioni parziali sull’ambiente
#
# Fornisce al controller una rappresentazione osservabile dello stato
#
# Normalizza i valori per l’apprendimento evolutivo
#
# Nota concettuale
# I sensori impongono un vincolo informativo: il robot non ha accesso allo stato completo.

def compute_sensors(robot, enemy, arena_size):
    dx = enemy.x - robot.x
    dy = enemy.y - robot.y

    distance = math.hypot(dx, dy) / arena_size
    angle_to_enemy = math.atan2(dy, dx)
    relative_angle = angle_to_enemy - robot.angle

    wall_front = min(
        robot.x / arena_size,
        (arena_size - robot.x) / arena_size,
        robot.y / arena_size,
        (arena_size - robot.y) / arena_size,
    )

    return [
        distance,
        math.sin(relative_angle),
        math.cos(relative_angle),
        wall_front,
        robot.energy / 100.0,
        enemy.energy / 100.0,
    ]
