'''A script that runs a game where the simple agent searches optimal path to powerup'''
import pommerman
from pommerman import agents


def main():
    '''Simple function to bootstrap a game.

       Use this as an example to set up your training env.
    '''
    # Print all possible environments in the Pommerman registry
    # TODO: once Search-v0 env is created, update registry
    print(pommerman.REGISTRY)

    # Create a set of agents (minimum two agents, maximum four agents)
    agent_list = [
        # TODO: replace SimpleAgent with a custom agent called SearchAgent
        agents.SimpleAgent(),
        agents.PlayerAgent(),
    ]

    # Make the "One-versus-One" environment using the agent list
    # TODO: replace this environment with a custom env called 'Search-v0'
    env = pommerman.make('OneVsOne-v0', agent_list)

    # Run the episodes just like OpenAI Gym
    num_episodes = 3  # change this to test how consistent the Search Agent in more episodes
    for i_episode in range(num_episodes):
        state = env.reset()
        done = False
        while not done:
            env.render()
            actions = env.act(state)
            state, reward, done, info = env.step(actions)
        print('Episode {} finished'.format(i_episode))
    env.close()


if __name__ == '__main__':
    main()
