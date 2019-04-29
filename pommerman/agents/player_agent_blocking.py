"""
This variant is blocking, that is the game pauses for keyboard input.
"""

from time import time
import click

from . import BaseAgent
from .. import characters
from .. import constants

# keypad control codes
K_PREFIX = '\x1b'
K_RT = '[C'
K_LF = '[D'
K_UP = '[A'
K_DN = '[B'


class PlayerAgentBlocking(BaseAgent):
    """Block for keyboard input."""

    def __init__(self, character=characters.Bomber, agent_control='arrows'):
        super(PlayerAgentBlocking, self).__init__(character)
        self.agent_control = agent_control

    def act(self, obs, action_space):
        key = click.getchar()
        if self.agent_control == 'arrows':
            if key == K_RT + K_PREFIX: return constants.Action.Right.value
            if key == K_LF + K_PREFIX: return constants.Action.Left.value
            if key == K_UP + K_PREFIX: return constants.Action.Up.value
            if key == K_DN + K_PREFIX: return constants.Action.Down.value
            if key == ' ': return constants.Action.Bomb.value
            return constants.Action.Stop.value

        if self.agent_control == 'wasd':
            if key == 'd': return constants.Action.Right.value
            if key == 'a': return constants.Action.Left.value
            if key == 'w': return constants.Action.Up.value
            if key == 's': return constants.Action.Down.value
            if key == 'e': return constants.Action.Bomb.value
            if key == 'q': return constants.Action.Stop.value
            return constants.Action.Stop.value
