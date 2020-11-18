'''Entry point into the pommerman module'''
import gym
import inspect
from . import agents
from . import configs
from . import constants
from . import forward_model
from . import helpers
from . import utility
from . import network

gym.logger.set_level(40)
REGISTRY = []


def _register(env_setup=None):
    global REGISTRY

    for name, f in inspect.getmembers(configs, inspect.isfunction):
        if (not name.endswith('_env')) or (name == 'search_v0_env' and env_setup is None):
            continue

        config = f(env_setup)
        
        if (config['env_id'] in REGISTRY):
            continue
        
        gym.envs.registration.register(
            id=config['env_id'],
            entry_point=config['env_entry_point'],
            kwargs=config['env_kwargs']
        )
        REGISTRY.append(config['env_id'])


# Register environments with gym
_register()


def make(config_id, agent_list, game_state_file=None, render_mode='human', env_setup=None):
    '''Makes the pommerman env and registers it with gym'''

    if (env_setup is not None):
        _register(env_setup)

    assert config_id in REGISTRY, "Unknown configuration '{}'. " \
        "Possible values: {}".format(config_id, REGISTRY)
    env = gym.make(config_id)

    for id_, agent in enumerate(agent_list):
        assert isinstance(agent, agents.BaseAgent)
        # NOTE: This is IMPORTANT so that the agent character is initialized
        agent.init_agent(id_, env.spec._kwargs['game_type'])

    env.set_agents(agent_list)
    env.set_init_game_state(game_state_file)
    env.set_render_mode(render_mode)
    return env
    
from . import cli