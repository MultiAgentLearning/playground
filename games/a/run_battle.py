"""Run a battle among agents.

Call this with a config and a list of docker files representing agents. The script will start separate threads
to operate the agents and then report back the result.

1. We need something that will load agents into an agent container.
2. That agent container *could* be a model or it could be a human or a docker or w/e.
3. The environment itself won't know this. It will only know that it can give this thing observations and get back actions.
"""
import agents
import configs
import utility
import atexit
import functools

import gym
import tensorflow as tf

import docker
client = docker.from_env()

def clean_up_agents(agents):
    """Stops all agents"""
    return [agent.stop() for agent in agents]

if __name__=="__main__":
    FLAGS = tf.app.flags.FLAGS
    tf.app.flags.DEFINE_string('config', 'pommerman_testFFA', 'Configuration to execute.')
    tf.app.flags.DEFINE_string(
        'agents',
        'random::null,random::null,random::null,docker::dennybritz/env-test',
        # 'player::arrows,random::null,random::null,random::null',
        'Comma delineated list of agent types and docker locations to run the agents.')
    # TODO: Incoporate the resource requirements.

    config = utility.AttrDict(getattr(configs, FLAGS.config)())
    _agents = []
    for agent_id, agent_info in enumerate(FLAGS.agents.split(',')):
        agent = config.agent(agent_id)
        agent_type, agent_control = agent_info.split('::')
        assert agent_type in ['player', 'random', 'docker']
        if agent_type == 'player':
            assert agent_control in ['arrows']
            on_key_press, on_key_release = utility.get_key_control(agent_control)
            _agents.append(agents.PlayerAgent(
                agent, utility.KEY_INPUT, on_key_press=on_key_press, on_key_release=on_key_release)
            )
            print('player is %d' % agent_id)
        elif agent_type == 'random':
            _agents.append(agents.RandomAgent(agent))
        elif agent_type == 'docker':
            agent = agents.DockerAgent(
                agent,
                docker_image=agent_control,
                docker_client=client,
                port=agent_id+1000)
            _agents.append(agent)

    print(config.env_kwargs)
    gym.envs.registration.register(
        id=config.env_id,
        entry_point=config.env_entry_point,
        kwargs=config.env_kwargs
    )
    env = config.env(**config.env_kwargs)
    env.seed(0)
    env.set_agents(_agents)

    atexit.register(functools.partial(clean_up_agents, _agents))

    print("Starting the Game.")
    obs = env.reset()
    steps = 0
    done = False
    while not done:
        steps += 1
        env.render()
        actions = env.act(obs)
        obs, reward, done, info = env.step(actions)

    print('Final Result: ', info)
    env.close()
