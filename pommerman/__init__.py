import gym
import inspect
from . import configs
from . import utility
from . import agents

# servers = os.environ.get('PLAYGROUND_BATTLE_SERVERS', ','.join(['http://localhost']*4)).split(',')

registry = None


def _register():
    local_registry = []
    for name, f in inspect.getmembers(configs, inspect.isfunction):
        config = f()
        gym.envs.registration.register(
            id=config['env_id'],
            entry_point=config['env_entry_point'],
            kwargs=config['env_kwargs']
        )
        local_registry.append(config['env_id'])
    return local_registry


def make(config_id, agent_list, game_state_file=None):
    assert config_id in registry
    env = gym.make(config_id)

    for idx, _agent in enumerate(agent_list):
        assert isinstance(_agent, agents.BaseAgent)
        # @NOTE: This is IMPORTANT so that the agent character is initialized
        _agent.init_agent(idx, env.spec._kwargs['game_type'])

    env.set_agents(agent_list)
    env.set_init_game_state(game_state_file)
    return env


# Register environments with gym
registry = _register()
