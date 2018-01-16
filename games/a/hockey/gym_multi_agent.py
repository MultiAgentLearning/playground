"""Utilities to make Gym more friendly to multi-agent. 

This should not be in this directory. It's here right now because it's easier this way
and the module may not exist pending what we do with this abstraction layer and question
of Gym vs Unity.
"""
import numpy as np

import gym
from gym.spaces import prng


class MultiDiscrete(gym.Space):
    """Similar to Gym's MultiDiscrete but properly handles the multi agent case.

    Args:
      array_of_param_array: A list of discrete action ranges, e.g. [[0, 4], [0, 1], [-5, 5]].
        For each range, the first value is considered the min, the second the max.
      num_agents: The number of agents for which this space is being applied.
    """
    def __init__(self, array_of_param_array, num_agents):
        self.low = np.array([x[0] for x in array_of_param_array])
        self.high = np.array([x[1] for x in array_of_param_array])
        self.num_discrete_space = self.low.shape[0]
        self.num_agents = num_agents

    def sample(self):
        """For each agent, returns an array with one sample from each discrete action space."""
        samples = []
        random_array = prng.np_random.rand(self.num_discrete_space * self.num_agents)
        for num_agent in range(self.num_agents):
            _random_array = random_array[num_agent*self.num_discrete_space:(num_agent+1)*self.num_discrete_space]
            samples.append([
                int(x) for x in np.floor(np.multiply((self.high - self.low + 1.), _random_array) + self.low)
            ])
        return samples

    def contains(self, x):
        """Checks if the input value is in the range.

        Args:
          x: A list where each num_discrete_space-sized entry represents an agent's actions.

        Returns whether all of the input values are in the correct range.
        """
        for arr in x:
            if len(arr) != self.num_discrete_space:
                return False

            arr = np.array(arr)
            if not (arr >= self.low).all() or not (arr >= self.high).all():
                return False
        return True

    @property
    def shape(self):
        return np.array([self.num_agents, self.num_discrete_space])

    def __repr__(self):
        return "MultiAgentMultiDiscrete: %d x %d" % (self.num_agents, self.num_discrete_space)

    def __eq__(self, other):
        return all([
            np.array_equal(self.low, other.low),
            np.array_equal(self.high, other.high),
            self.num_agents == other.num_agents
        ])
