from .. import characters


class BaseAgent:
    """Parent abstract Agent."""

    def __init__(self, agent=characters.Bomber):
        self._agent = agent

    def __getattr__(self, attr):
        return getattr(self._agent, attr)

    def act(self, obs, action_space):
        raise NotImplementedError()

    def init_agent(self, id, game_type):
        self._agent = self._agent(id, game_type)

    @staticmethod
    def has_user_input():
        return False

    def shutdown(self):
        pass

