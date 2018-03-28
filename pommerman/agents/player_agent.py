from . import BaseAgent
from .. import characters


class PlayerAgent(BaseAgent):
    """The Player Agent that lets the user control a character."""

    def __init__(self, agent=characters.Bomber, agent_control='arrows'):
        super(PlayerAgent, self).__init__(agent)

        ##
        # @NOTE: DONOT move this import outside the constructor. It will
        # not work in headless environments like a Docker container
        # and prevents Pommerman from running
        #
        from pyglet.window import key
        self._controls = {
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

        assert agent_control in self._controls.keys()
        self._key_input = {'curr': 0}
        self._control_type = agent_control

    def act(self, obs, action_space):
        return self._key_input['curr']

    @staticmethod
    def has_user_input():
        return True

    def on_key_press(self, k, mod):
        self._key_input['curr'] = self._controls[self._control_type].get(k, 0)

    def on_key_release(self, k, mod):
        self._key_input['curr'] = 0
