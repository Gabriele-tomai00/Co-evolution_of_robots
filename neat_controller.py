#    Gabriele Tomai
#    Student ID: IN2300006
#    Degree Program: Computer Engineering

import neat
from sensors import Sensors

class NEATController:
    """
    Controller based on a NEAT-evolved neural network.
    It maps sensor inputs to high-level robot actions.
    """

    def __init__(self, genome, config):
        # Create a feed-forward neural network from the genome
        self.net = neat.nn.FeedForwardNetwork.create(genome, config)

    def decide(self, robot, arena):
        """
        Decide the next action for the robot given the current arena state.
        """

        # Read sensor values
        inputs = Sensors.get(robot, arena)

        # Forward pass through the neural network
        outputs = self.net.activate(inputs)

        # Interpret network outputs
        action = self._decode_outputs(outputs)

        return action

    def _decode_outputs(self, outputs):
        """
        Convert raw neural network outputs into a structured action.
        """

        # Output 0: movement command (-1 backward, +1 forward)
        move = outputs[0]

        # Output 1: rotation command (-1 left, +1 right)
        turn = outputs[1]

        # Output 2: shooting decision
        shoot = outputs[2] > 0.5

        return {
            "move": move,
            "turn": turn,
            "shoot": shoot
        }
