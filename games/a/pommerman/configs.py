from . import envs
from . import characters

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
        'num_wood': envs.utility.NUM_WOOD,
        'num_items': envs.utility.NUM_ITEMS,
        'first_collapse': envs.utility.FIRST_COLLAPSE,
        'max_steps': envs.utility.MAX_STEPS
    }
    print(env_kwargs)
    agent = characters.Agent
    return locals()
