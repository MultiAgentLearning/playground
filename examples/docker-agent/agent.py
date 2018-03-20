"""Implementation of a simple deterministic agent using Docker."""

import pommerman
from pommerman.runner import DockerAgentRunner


class Agent(DockerAgentRunner):
    def __init__(self):
        self._agent = pommerman.make_agent('ffa_v0', 'test::agents.SimpleAgent')

    def act(self, observation, action_space):
        return self._agent.act(observation, action_space)
