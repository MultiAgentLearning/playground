''' Helpers'''
import os
from .. import agents

USE_GAME_SERVERS = os.getenv("PLAYGROUND_USE_GAME_SERVERS")
GAME_SERVERS = {id_: os.getenv("PLAYGROUND_GAME_INSTANCE_%d" % id_)
                for id_ in range(4)}


# NOTE: This routine is meant for internal usage.
def make_agent_from_string(agent_string, agent_id, docker_env_dict=None):
    '''Internal helper for building an agent instance'''
    
    agent_type, agent_control = agent_string.split("::")

    assert agent_type in ["player", "playerblock", "simple", "random", "docker", "http" , "test", "tensorforce"]

    agent_instance = None

    if agent_type == "player":
        agent_instance = agents.PlayerAgent(agent_control=agent_control)
    elif agent_type == "playerblock":
        agent_instance = agents.PlayerAgentBlocking(agent_control=agent_control)
    elif agent_type == "simple":
        agent_instance = agents.SimpleAgent()
    elif agent_type == "random":
        agent_instance = agents.RandomAgent()
    elif agent_type == "docker":
        port = agent_id + 1000
        if not USE_GAME_SERVERS:
            server = 'http://localhost'
        else:
            server = GAME_SERVERS[agent_id]
        assert port is not None
        agent_instance = agents.DockerAgent(
            agent_control, port=port, server=server, env_vars=docker_env_dict)
    elif agent_type == "http":
        host, port = agent_control.split(":")
        agent_instance = agents.HttpAgent(port=port, host=host)
    elif agent_type == "test":
        agent_instance = eval(agent_control)()
    elif agent_type == "tensorforce":
        agent_instance = agents.TensorForceAgent(algorithm=agent_control)

    return agent_instance
