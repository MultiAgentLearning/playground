import gym
import inspect
import os
import docker
from . import configs
from . import utility
from . import agents

client = docker.from_env()
servers = os.environ.get('PLAYGROUND_BATTLE_SERVERS', ','.join(['http://localhost']*4)).split(',')


def register():
    for name, f in inspect.getmembers(configs, inspect.isfunction):
        config = f()
        gym.envs.registration.register(
            id=config['env_id'],
            entry_point=config['env_entry_point'],
            kwargs=config['env_kwargs']
        )


def make_agent(config_string, agent_string, agent_id=-1, docker_env_dict=None):
    config = utility.AttrDict(getattr(configs, config_string)())

    agent = config.agent(agent_id, config.game_type)
    agent_type, agent_control = agent_string.split("::")

    assert agent_type in ["player", "random", "docker", "test"]

    if agent_type == "player":
        agent_instance = agents.PlayerAgent(agent, agent_control)
    elif agent_type == "random":
        agent_instance = agents.RandomAgent(agent)
    elif agent_type == "docker":
        agent_instance = agents.DockerAgent(
            agent,
            docker_image=agent_control,
            docker_client=client,
            server=servers[agent_id],
            port=agent_id + 1000,
            env_vars=docker_env_dict)
    elif agent_type == "test":
        agent_instance = eval(agent_control)(agent)

    return agent_instance


def make(config_string, agent_string, docker_env_string='', game_state_file=None):
    config = utility.AttrDict(getattr(configs, config_string)())
    env = config.env(**config.env_kwargs)

    env_vars = {}
    if "," in docker_env_string:
        for agent in docker_env_string.split(","):
            agent_id = int(agent.split(':')[0])
            env_vars[agent_id] = {}
            for pair in agent.split(':')[1:]:
                key, value = pair.split('=')
                env_vars[agent_id][key] = value

    _agents = []
    for agent_id, agent_string in enumerate(agent_string.split(',')):
        agent_instance = make_agent(config_string, agent_string, agent_id, env_vars.get(agent_id))
        _agents.append(agent_instance)

    env.set_agents(_agents)
    env.set_init_game_state(game_state_file)
    return env


# Register environments with gym
register()
