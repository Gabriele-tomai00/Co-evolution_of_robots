import math
from arena import Arena
from robot import Robot
from controllers import RandomController


def main():
    arena = Arena()

    robot_a = Robot(x=2, y=2, angle=0)
    robot_b = Robot(x=18, y=18, angle=math.pi)

    ctrl_a = RandomController()
    ctrl_b = RandomController()

    result = arena.run_match(robot_a, robot_b, ctrl_a, ctrl_b)

    if result == 1:
        print("Robot A wins")
    elif result == -1:
        print("Robot B wins")
    else:
        print("Draw")


if __name__ == "__main__":
    main()
