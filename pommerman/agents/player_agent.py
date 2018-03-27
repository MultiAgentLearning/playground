from pyglet.window import key

from . import BaseAgent
from .. import characters


CONTROLS = {
    'arrows': {
        key.UP: 1,
        key.DOWN: 2,
        key.LEFT: 3,
        key.RIGHT: 4,
        key.SPACE: 5,
        key.M: 6  # In Pommerman, this will freeze the game.
    },
    'wasd': {
        key.W: 1,
        key.S: 2,
        key.A: 3,
        key.D: 4,
        key.E: 5,
        key.Q: 6  # In Pommerman, this will freeze the game.
    }
}


class PlayerAgent(BaseAgent):
    """The Player Agent that lets the user control a character."""

    def __init__(self, agent=characters.Agent, key_control='arrows'):
        super(PlayerAgent, self).__init__(agent)

        assert key_control in CONTROLS.keys()
        self._key_input = {'curr': 0}
        self._key_control = key_control

    def act(self, obs, action_space):
        return self._key_input['curr']

    @staticmethod
    def has_user_input():
        return True

    def on_key_press(self, k, mod):
        self._key_input['curr'] = self._controls[self._key_control].get(k, 0)

    def on_key_release(self, k, mod):
        self._key_input['curr'] = 0
