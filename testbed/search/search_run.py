'''A script that runs a game where the simple agent searches optimal path to powerup'''
import pommerman
from pommerman import agents
import json


def main(env_setup_dict):
    '''Simple function to bootstrap a game.'''

    # Create a Search Agent
    agent_list = [
        agents.SearchAgent()
    ]

    # Make the "Search" environment using the agent list and setup inputs
    env = pommerman.make('Search-v0', agent_list, env_setup=env_setup_dict)

    # The following print statement should include Search-v0
    # print(pommerman.REGISTRY)

    # Run the episodes just like OpenAI Gym
    num_episodes = 1  # change this to test how consistent the Search Agent in more episodes
    for i_episode in range(num_episodes):
        state = env.reset()
        done = False
        while not done:
            env.render()
            actions = env.act(state)
            state, reward, done, info = env.step(actions)
        print('Episode {} finished'.format(i_episode))
        # print(state)
        # print(reward)
        # print(info)
    env.close()


if __name__ == '__main__':
    with open('env_setup.json', 'r') as f:
        env_setup_dict = json.load(f)

    for attribute in env_setup_dict:
        print(attribute, env_setup_dict[attribute])

    main(env_setup_dict)
