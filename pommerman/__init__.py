import os
import docker
from . import configs
from . import utility
from . import agents
from . import agent_classes

client = docker.from_env()
servers = os.environ.get('PLAYGROUND_BATTLE_SERVERS', ','.join(['http://localhost']*4)).split(',')


def make(config_string, agent_string, docker_env_string=''):
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
    for agent_id, agent_info in enumerate(agent_string.split(',')):
        agent = config.agent(agent_id, config.game_type)
        agent_type, agent_control = agent_info.split("::")

        assert agent_type in ["player", "random", "docker", "test"]

        ##
        # @NOTE: These could be abstracted into a `make_agent` function
        # but the current logic is simple enough to keep here
        #
        if agent_type == "player":
            assert agent_control in ["arrows"]
            on_key_press, on_key_release = utility.get_key_control(agent_control)
            agent_instance = agent_classes.PlayerAgent(
                agent, utility.KEY_INPUT, on_key_press=on_key_press, on_key_release=on_key_release)
        elif agent_type == "random":
            agent_instance = agent_classes.RandomAgent(agent)
        elif agent_type == "docker":
            agent_instance = agent_classes.DockerAgent(
                agent,
                docker_image=agent_control,
                docker_client=client,
                server=servers[agent_id],
                port=agent_id+1000,
                env_vars=env_vars.get(agent_id))
        elif agent_type == "test":
            agent_instance = eval(agent_control)(agent)

        _agents.append(agent_instance)

    env.set_agents(_agents)

    # @TODO fix this to be compatible with `gym.make`
    # gym.envs.registration.register(
    #     id=config.env_id,
    #     entry_point=config.env_entry_point,
    #     kwargs=config.env_kwargs
    # )

    return env
