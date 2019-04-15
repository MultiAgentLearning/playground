from time import time
import click

from . import BaseAgent
from .. import characters
from .. import constants


class PlayerAgentBlocking(BaseAgent):
    """Block for keyboard input."""

    def __init__(self, character=characters.Bomber, agent_control='arrows'):
        super(PlayerAgentBlocking, self).__init__(character)
        self._character.agent_image = 'agent-player'
        self.agent_control=agent_control

    def act(self, obs, action_space):
        key = click.getchar()
        #key = click.pause()
        #print(key,repr(key))
        if self.agent_control=='arrows':
            if key=='\x1b[C': return constants.Action.Right.value
            if key=='\x1b[D': return constants.Action.Left.value
            if key=='\x1b[A': return constants.Action.Up.value
            if key=='\x1b[B': return constants.Action.Down.value
            if key==' ': return constants.Action.Bomb.value
            return constants.Action.Stop.value

        if self.agent_control=='wasd':
            if key=='d': return constants.Action.Right.value
            if key=='a': return constants.Action.Left.value
            if key=='w': return constants.Action.Up.value
            if key=='s': return constants.Action.Down.value
            if key=='e': return constants.Action.Bomb.value
            if key=='q': return constants.Action.Stop.value
            return constants.Action.Stop.value

