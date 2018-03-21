"""Run a battle among agents.

Call this with a config, a game, and a list of agents. The script will start separate threads to operate the agents
and then report back the result.

An example with all four test agents running ffa:
python run_battle.py --agents=test::agents.SimpleAgent,test::agents.SimpleAgent,test::agents.SimpleAgent,test::agents.SimpleAgent --config=ffa_v0

An example with one player, two random agents, and one test agent:
python run_battle.py --agents=player::arrows,test::agents.SimpleAgent,random::null,random::null --config=ffa_v0

An example with a docker agent:
python run_battle.py --agents=player::arrows,docker::pommerman/test-agent,random::null,random::null --config=ffa_v0
"""
import atexit
import functools
import random
import time

import argparse
import numpy as np

from .. import make


def clean_up_agents(agents):
    """Stops all agents"""
    return [agent.shutdown() for agent in agents]


def run(args, num_times=1, seed=None):
    config = args.config
    agents_string = args.agents
    record_dir = args.record_dir
    agent_env_vars = args.agent_env_vars

    env = make(config, agents_string, agent_env_vars)

    def _run(seed, record_dir=None):
        env.seed(seed)
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
        return info

    infos = []
    times = []
    for i in range(num_times):
        start = time.time()
        if seed is None:
            seed = random.randint(0, 1e6)
        np.random.seed(seed)
        random.seed(seed)

        if record_dir is not None:
            infos.append(_run(seed, record_dir + '/%d' % (i+1)))
        else:
            infos.append(_run(seed, record_dir))
        times.append(time.time() - start)
        print("Game Time: ", times[-1])

    env.close()
    atexit.register(functools.partial(clean_up_agents, env._agents))
    return infos


def main():
    parser = argparse.ArgumentParser(description='Playground Flags.')
    parser.add_argument('--game',
                        default='pommerman',
                        help='Game to choose.')
    parser.add_argument('--config',
                        default='ffa_v0',
                        help='Configuration to execute.')
    parser.add_argument('--agents',
                        # default='test::agents.SimpleAgent,test::agents.SimpleAgent,test::agents.SimpleAgent,test::agents.SimpleAgent',
                        # default='player::arrows,test::agents.SimpleAgent,test::agents.SimpleAgent,test::agents.SimpleAgent',
                        default='docker::pommerman/simple-agent,test::agents.SimpleAgent,test::agents.SimpleAgent,test::agents.SimpleAgent',
                        help='Comma delineated list of agent types and docker locations to run the agents.')
    parser.add_argument('--agent_env_vars',
                        help="Comma delineated list of agent environment vars to pass to Docker. This is only for the Docker Agent. An example is '0:foo=bar:baz=lar,3:foo=lam', which would send two arguments to Docker Agent 0 and one to Docker Agent 3.",
                        default="")
    parser.add_argument('--record_dir',
                        help="Directory to record the PNGs of the game. Doesn't record if None.")
    parser.add_argument('--render',
                        default=True,
                        help="Whether to render or not. Defaults to True.")
    args = parser.parse_args()
    run(args)


if __name__ == "__main__":
    main()
