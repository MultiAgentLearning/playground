'''Entry point into the agents module set'''
from .base_agent import BaseAgent
from .docker_agent import DockerAgent
from .http_agent import HttpAgent
from .player_agent import PlayerAgent
from .player_agent_blocking import PlayerAgentBlocking
from .random_agent import RandomAgent
from .random_agent import SmartRandomAgent
from .random_agent import SmartRandomAgentNoBomb
from .random_agent import SlowRandomAgentNoBomb
from .simple_agent import SimpleAgent
from .tensorforce_agent import TensorForceAgent
from .model import CNN_LSTM

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))
