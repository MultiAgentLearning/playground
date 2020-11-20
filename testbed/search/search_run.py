'''A script that runs a game where the simple agent searches optimal path to powerup'''
import pommerman
from pommerman import agents
import json
import time


def main(env_setup_dict):
    '''Simple function to bootstrap a game.'''

    # Create a Search Agent
    agent_list = [
        agents.SearchAgent()
    ]

    # Make the "Search" environment using the agent list and setup parameters
    env = pommerman.make('Search-v0', agent_list, env_setup=env_setup_dict)

    # Construct a clean slate environment
    state = env.reset()
    done = False

    # Begin timing program
    start_time = time.time()

    # Increase time limit by 2 seconds to account for noticeable lag in rendering GUI
    time_limit = env_setup_dict['max_duration_seconds'] + 2

    # Iterate through agent actions and environment observations
    while not done:
        # Monitor time elapsed
        current_time = time.time()
        elapsed_time = current_time - start_time

        # Terminate program if time limit exceeded
        if elapsed_time > time_limit:
            print("Terminated the program because time limit exceeded.")
            break

        env.render()
        actions = env.act(state)
        state, reward, done, info = env.step(actions)
        # print(state)
        # print(reward)
        # print(info)

    return (state, reward, done, info)

    env.close()


if __name__ == '__main__':
    with open('env_setup.json', 'r') as f:
        env_setup_dict = json.load(f)

    for attribute in env_setup_dict:
        print(attribute, env_setup_dict[attribute])

    result = main(env_setup_dict)
    hasSucceeded = result[2]

    if hasSucceeded:
        info = result[3]
        print(info)
    else:
        print('Failed')
