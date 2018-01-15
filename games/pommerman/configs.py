from __future__ import absolute_import
from __future__ import division
from __future__ import print_function


import gym

from envs import v0


def testFFA():
    env = v0.Pomme
    ret = locals()
    gym.envs.registration.register(
        id='Pomme-v0',
        entry_point='v0:Pomme',
    )
    return ret
