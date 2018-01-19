from . import envs
from . import agents

import gym


# TODO: Remove the pommerman_ and make it universal to the configs here.
def pommerman_testFFA():
    env = envs.v0.Pomme
    env_entry_point = 'envs:v0:Pomme'
    env_id = 'Pomme-v0'
    env_kwargs = {
        'game_type': envs.utility.GameType.FFA,
        'board_size': envs.utility.BOARD_SIZE,
        'num_rigid': envs.utility.NUM_RIGID,
        'num_passage': envs.utility.NUM_PASSAGE,
        'num_items': envs.utility.NUM_ITEMS,
    }
    print(env_kwargs)
    agent = agents.Agent
    return locals()
