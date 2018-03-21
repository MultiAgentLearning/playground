from . import BaseAgent


class PlayerAgent(BaseAgent):
    """The Player Agent that lets the user control a character."""
    def __init__(self, agent, key_input, on_key_press, on_key_release):
        self._agent = agent
        self._key_input = key_input
        self.on_key_press = on_key_press
        self.on_key_release = on_key_release

    def act(self, obs, action_space):
        return self._key_input['curr']

    @staticmethod
    def has_key_input():
        return True
