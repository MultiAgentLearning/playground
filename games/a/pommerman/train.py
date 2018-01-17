"""Run training.

TODO: ... Everything.
"""

import a
import tensorflow as tf


if __name__=="__main__":
    FLAGS = tf.app.flags.FLAGS
    tf.app.flags.DEFINE_string('config', 'testFFA', 'Configuration to execute.')
    tf.app.flags.DEFINE_string(
        'agents',
        'player:arrows,random:null,docker:/tmp/agent3.docker,docker:/tmp/agent3.docker',
        'Comma delineated list of agent types and docker locations to run the agents.')

    config = utility.AttrDict(getattr(a.pommerman.configs, FLAGS.config)())
    agents = []
    for agent_id, agent_info in enumerate(FLAGS.agents.split(',')):
        agent = a.pommerman.agent.Agent(agent_id)
        agent_type, agent_control = agent_info.split(':')
        assert agent_control in ['player', 'random', 'docker']
        if agent_type == 'player':
            assert agent_control in ['arrows']
            _, _, key_input = a.utility.get_key_control(agent_control)
            agents.append(a.agent.PlayerAgent(agent, key_input=key_input))
        elif agent_type == 'random':
            agents.append(a.agent.RandomAgent(agent))
        elif agent_type == 'docker':
            agents.append(a.agent.DockerAgent(agent, docker_loc=agent_control))

    gym.envs.registration.register(
        id=config.env_id,
        entry_point=config.env_entry_point
        kwargs=config.env_kwargs
    )
    env = config.env()
    env.seed(0)
    env.set_agents(agents)

    print("Starting the Game.")
    obs = env.reset()
    steps = 0
    done = False
    while not done:
        steps += 1
        env.render()
        actions = env.act()
        obs, reward, done, info = env.step(actions)

    print('Final Result: ', info)
    env.close()
