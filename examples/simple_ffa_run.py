'''An example to show how to set up an pommerman game programmatically'''
import pommerman
from pommerman import agents


def main():
    '''Simple function to bootstrap a game.
       
       Use this as an example to set up your training env.
    '''
    # Print all possible environments in the Pommerman registry
    print(pommerman.REGISTRY)

    # Create a set of agents (exactly four)
    agent_list = [
        agents.SimpleAgent(),
        agents.RandomAgent(),        
        agents.RandomAgent(),
        #agents.DockerAgent("multiagentlearning/hakozakijunctions", port=12345),
        #agents.DockerAgent("multiagentlearning/eisenach", port=12345),
        agents.DockerAgent("multiagentlearning/skynet955", port=12345),
    ]
    # Make the "Free-For-All" environment using the agent list
    env = pommerman.make('PommeTeamCompetition-v1', agent_list)

    # Run the episodes just like OpenAI Gym
    for i_episode in range(1):
        state = env.reset()
        done = False
        while not done:
            env.render()
            actions = env.act(state)
            state, reward, done, info = env.step(actions)
        print('Episode {} finished'.format(i_episode))
        print("Final Result: ", info)
    env.close()


if __name__ == '__main__':
    main()
