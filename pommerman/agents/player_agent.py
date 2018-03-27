from pyglet.window import key

from . import BaseAgent


class PlayerAgent(BaseAgent):
    """The Player Agent that lets the user control a character."""
    def __init__(self, agent, control):
        super(PlayerAgent, self).__init__(agent)
        self._key_input = {'curr': 0}
        assert control == 'arrows', 'No input besides "arrows" implemented yet.'

    def act(self, obs, action_space):
        return self._key_input['curr']

    @staticmethod
    def has_key_input():
        return True

    def on_key_press(self, k, mod):
        self._key_input['curr'] = {
            key.UP: 1,
            key.DOWN: 2,
            key.LEFT: 3,
            key.RIGHT: 4,
            key.SPACE: 5,
            key.A: 6 # In Pommerman, this will freeze the game.
        }.get(k, 0)

    def on_key_release(self, k, mod):
        self._key_input['curr'] = 0
