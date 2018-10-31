"""Run a battle among agents.

Call this with a config, a game, and a list of agents. The script will start separate threads to operate the agents
and then report back the result.

An example with all four test agents running ffa:
python run_battle.py --agents=test::agents.SimpleAgent,test::agents.SimpleAgent,test::agents.SimpleAgent,test::agents.SimpleAgent --config=PommeFFACompetition-v0

An example with one player, two random agents, and one test agent:
python run_battle.py --agents=player::arrows,test::agents.SimpleAgent,random::null,random::null --config=PommeFFACompetition-v0

An example with a docker agent:
python run_battle.py --agents=player::arrows,docker::pommerman/test-agent,random::null,random::null --config=PommeFFACompetition-v0
"""
import atexit
from datetime import datetime
import os
import random
import sys
import time

import argparse
import numpy as np

from .. import helpers
from .. import make
from pommerman import utility


def run(args, num_times=1, seed=None):
    '''Wrapper to help start the game'''
    config = args.config
    record_pngs_dir = args.record_pngs_dir
    record_json_dir = args.record_json_dir
    agent_env_vars = args.agent_env_vars
    game_state_file = args.game_state_file
    render_mode = args.render_mode
    do_sleep = args.do_sleep

    agents = [
        helpers.make_agent_from_string(agent_string, agent_id)
        for agent_id, agent_string in enumerate(args.agents.split(','))
    ]

    env = make(config, agents, game_state_file, render_mode=render_mode)

    def _run(record_pngs_dir=None, record_json_dir=None):
        '''Runs a game'''
        print("Starting the Game.")
        if record_pngs_dir and not os.path.isdir(record_pngs_dir):
            os.makedirs(record_pngs_dir)
        if record_json_dir and not os.path.isdir(record_json_dir):
            os.makedirs(record_json_dir)

        obs = env.reset()
        done = False

        while not done:
            if args.render:
                env.render(
                    record_pngs_dir=record_pngs_dir,
                    record_json_dir=record_json_dir,
                    do_sleep=do_sleep)
            if args.render is False and record_json_dir:
                env.save_json(record_json_dir)
                time.sleep(1.0 / env._render_fps)
            actions = env.act(obs)
            obs, reward, done, info = env.step(actions)

        print("Final Result: ", info)
        if args.render:
            env.render(
                record_pngs_dir=record_pngs_dir,
                record_json_dir=record_json_dir,
                do_sleep=do_sleep)
            if do_sleep:
                time.sleep(5)
            env.render(close=True)
            
        if args.render is False and record_json_dir:
            env.save_json(record_json_dir)
            time.sleep(1.0 / env._render_fps)

        if record_json_dir:
            finished_at = datetime.now().isoformat()
            _agents = args.agents.split(',')
            utility.join_json_state(record_json_dir, _agents, finished_at,
                                    config, info)

        return info

    if seed is None:
        # Pick a random seed between 0 and 2^31 - 1
        seed = random.randint(0, np.iinfo(np.int32).max)
    np.random.seed(seed)
    random.seed(seed)
    env.seed(seed)

    infos = []
    times = []
    for i in range(num_times):
        start = time.time()

        record_pngs_dir_ = record_pngs_dir + '/%d' % (i+1) \
                           if record_pngs_dir else None
        record_json_dir_ = record_json_dir + '/%d' % (i+1) \
                           if record_json_dir else None
        infos.append(_run(record_pngs_dir_, record_json_dir_))

        times.append(time.time() - start)
        print("Game Time: ", times[-1])

    atexit.register(env.close)
    return infos


def main():
    '''CLI entry pointed used to bootstrap a battle'''
    simple_agent = 'test::agents.SimpleAgent'
    player_agent = 'player::arrows'
    docker_agent = 'docker::pommerman/simple-agent'

    parser = argparse.ArgumentParser(description='Playground Flags.')
    parser.add_argument(
        '--config',
        default='PommeFFACompetition-v0',
        help='Configuration to execute. See env_ids in '
        'configs.py for options.')
    parser.add_argument(
        '--agents',
        default=','.join([simple_agent] * 4),
        # default=','.join([player_agent] + [simple_agent]*3]),
        # default=','.join([docker_agent] + [simple_agent]*3]),
        help='Comma delineated list of agent types and docker '
        'locations to run the agents.')
    parser.add_argument(
        '--agent_env_vars',
        help='Comma delineated list of agent environment vars '
        'to pass to Docker. This is only for the Docker Agent.'
        " An example is '0:foo=bar:baz=lar,3:foo=lam', which "
        'would send two arguments to Docker Agent 0 and one '
        'to Docker Agent 3.',
        default="")
    parser.add_argument(
        '--record_pngs_dir',
        default=None,
        help='Directory to record the PNGs of the game. '
        "Doesn't record if None.")
    parser.add_argument(
        '--record_json_dir',
        default=None,
        help='Directory to record the JSON representations of '
        "the game. Doesn't record if None.")
    parser.add_argument(
        "--render",
        default=False,
        action='store_true',
        help="Whether to render or not. Defaults to False.")
    parser.add_argument(
        '--render_mode',
        default='human',
        help="What mode to render. Options are human, rgb_pixel, and rgb_array")
    parser.add_argument(
        '--game_state_file',
        default=None,
        help="File from which to load game state.")
    parser.add_argument(
        '--do_sleep',
        default=True,
        help="Whether we sleep after each rendering.")
    args = parser.parse_args()
    run(args)


if __name__ == "__main__":
    main()
