import copy
import numpy as np
from pommerman import agents
from . import BaseAgent
from .. import MCTS
from .. import constants
from .. import utility


class SmartAgent(BaseAgent):
    def __init__(self, model):
        super().__init__()
        self.memory = None
        self.model = model

    def act(self, obs, action_space):
        self.memory = utility.update_agent_memory(self.memory, obs)
        extended_obs = utility.combine_agent_obs_and_memory(self.memory, obs)
        action_prior = self.model.predict(extended_obs)
        return action_prior.argmax()