"""Run a battle among agents.

Call this with a config, a game, and a list of agents. The script will start separate threads to operate the agents
and then report back the result.

An example with all four test agents running ffa:
python run_battle.py --agents=test::a.pommerman.agents.SimpleAgent,test::a.pommerman.agents.SimpleAgent,test::a.pommerman.agents.SimpleAgent,test::a.pommerman.agents.SimpleAgent --config=ffa_v0

An example with one player, two random agents, and one test agent:
python run_battle.py --agents=player::arrows,test::a.pommerman.agents.SimpleAgent,random::null,random::null --config=ffa_v0

An example with a docker agent:
python run_battle.py --agents=player::arrows,docker::pommerman/test-agent,random::null,random::null --config=ffa_v0
"""
import a

import atexit
import functools
import os
import time

import argparse
import docker
import gym


client = docker.from_env()
servers = os.environ.get('PLAYGROUND_BATTLE_SERVERS', ','.join(['http://localhost']*4)).split(',')


def clean_up_agents(agents):
    """Stops all agents"""
    return [agent.shutdown() for agent in agents]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Playground Flags.')
    parser.add_argument('--game',
                        default='pommerman',
                        help='Game to choose.')
    parser.add_argument('--config',
                        default='ffa_v0',
                        help='Configuration to execute.')
    parser.add_argument('--agents',
                        # default='random::null,random::null,random::null,docker::pommerman/test-agent', 
                        # default='player::arrows,random::null,random::null,random::null',
                        # default='test::a.pommerman.agents.SimpleAgent,test::a.pommerman.agents.SimpleAgent,test::a.pommerman.agents.SimpleAgent,test::a.pommerman.agents.SimpleAgent',
                        default='player::arrows,test::a.pommerman.agents.SimpleAgent,test::a.pommerman.agents.SimpleAgent,test::a.pommerman.agents.SimpleAgent',
                        help='Comma delineated list of agent types and docker locations to run the agents.')
    parser.add_argument('--record_dir',
                        help="Directory to record the PNGs of the game. Doesn't record if None.")
    parser.add_argument('--render',
                        default=True,
                        help="Whether to render or not. Defaults to True.")
    args = parser.parse_args()

    game = getattr(a, args.game)
    configs = getattr(game, 'configs')
    config = a.utility.AttrDict(getattr(configs, args.config)())
    _agents = []
    for agent_id, agent_info in enumerate(args.agents.split(",")):
        agent = config.agent(agent_id, config.game_type)
        agent_type, agent_control = agent_info.split("::")
        assert agent_type in ["player", "random", "docker", "test"]
        if agent_type == "player":
            assert agent_control in ["arrows"]
            on_key_press, on_key_release = a.utility.get_key_control(agent_control)
            agent = a.agents.PlayerAgent(
                agent, a.utility.KEY_INPUT, on_key_press=on_key_press, on_key_release=on_key_release)
        elif agent_type == "random":
            agent = a.agents.RandomAgent(agent)
        elif agent_type == "docker":
            agent = a.agents.DockerAgent(
                agent,
                docker_image=agent_control,
                docker_client=client,
                server=servers[agent_id],
                port=agent_id+1000)
        elif agent_type == "test":
            agent = eval(agent_control)(agent)
        _agents.append(agent)

    gym.envs.registration.register(
        id=config.env_id,
        entry_point=config.env_entry_point,
        kwargs=config.env_kwargs
    )
    env = config.env(**config.env_kwargs)
    env.seed(0)
    env.set_agents(_agents)

    atexit.register(functools.partial(clean_up_agents, _agents))
    record_dir = args.record_dir

    print("Starting the Game.")
    obs = env.reset()
    steps = 0
    done = False
    while not done:
        steps += 1
        if args.render:
            env.render(record_dir=record_dir)
        actions = env.act(obs)
        obs, reward, done, info = env.step(actions)

    print("Final Result: ", info)
    if args.render:
        time.sleep(5)
        env.render(close=True)
    env.close()
