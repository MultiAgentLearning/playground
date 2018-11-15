from pommerman import make, agents
from . import BaseAgent
from .. import MCTS


class SmartAgent(BaseAgent):

    def __init__(self, training_env=None):
        super().__init__()
        self.modelled_env = training_env or \
                            make('PommeTeamCompetition-v0', agent_list=[agents.SimpleAgent() for _ in range(4)])   # 4 players

        self.history = None

    def build_history(self, agent_obs):
        # TODO: for Amy to finish
        raise NotImplementedError()

    def act(self, obs, action_space):

        # TODO: left some pseudo-code here, but general
        # TODO: idea here is simple
        pi = MCTS.perform_MCTS(self.modelled_env, self.agent_id)
        self.history = self.build_history(obs)
        training_pool.append((self.history, pi))
        return random.sample(list(range(6)), p=pi)


