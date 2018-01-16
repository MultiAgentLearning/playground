from __future__ import absolute_import
from __future__ import division
from __future__ import print_function


import gym

from envs import v0


def test1v1():
    env = v0.Hockey
    num_agents_per_team = 1
    ret = locals()
    gym.envs.registration.register(
        id='Hockey-v0',
        entry_point='v0:Hockey',
        kwargs={'num_agents_per_team': 1}
    )
    return ret
