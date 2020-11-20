'''A script that runs a game where the simple agent searches optimal path to powerup'''
import pommerman
from pommerman import agents
import json
import signal
import multiprocessing
import time
from search_algo_file import search


def main(env_setup_dict):
    '''Simple function to bootstrap a game.'''

    # Create a Search Agent
    agent_list = [
        agents.SearchAgent()
    ]

    # Make the "Search" environment using the agent list and setup parameters
    env = pommerman.make('Search-v0', agent_list, env_setup=env_setup_dict)

    # import implemented search algorithm
    search_function = None

    # Construct a clean slate environment
    initial_state = env.reset()
    done = False

    # Set time limit and start time
    time_limit = env_setup_dict['max_duration_seconds']
    start_time = time.time()

    # obtain list of actions to take from search algorithm
    actions = search(initial_state[0]['board'], initial_state[0]['position'])

    # Monitor time elapsed
    current_time = time.time()
    elapsed_time = current_time - start_time

    # Terminate program if time limit exceeded
    if elapsed_time > time_limit:
        print("Your algorithm has exceeded the time limit.")
        return ([], [], done, [])

    # Iterate through agent actions and environment observations
    for i in range(len(actions)):
        curr_action = [actions[i]]
        env.render()
        state, reward, done, info = env.step(curr_action)

    return (state, reward, done, info)

    env.close()


if __name__ == '__main__':
    with open('env_setup.json', 'r') as f:
        env_setup_dict = json.load(f)

    result = main(env_setup_dict)
    hasSucceeded = result[2]

    if hasSucceeded:
        info = result[3]
        print('The algorithm has succeeded!')
    else:
        print('The algorithm has failed.')
