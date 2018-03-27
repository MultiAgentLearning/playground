
class BaseAgent:
    """Parent abstract Agent."""

    def __init__(self, agent):
        self._agent = agent

    def __getattr__(self, attr):
        return getattr(self._agent, attr)

    def act(self, obs, action_space):
        raise NotImplementedError()

    @staticmethod
    def has_user_input():
        return False

    def shutdown(self):
        pass

