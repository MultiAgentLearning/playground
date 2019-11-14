'''An example to show how to set up an pommerman game programmatically'''
import os
import sys
import pommerman
from pommerman import agents
from pommerman.agents import random_agent, simple_agent_cautious_bomb

#ENV_ID='PommeFFACompetition-v0'
RENDER=False
N_game=20
ENV_ID="PommeTeamCompetition-v0"

def main():
    # Print all possible environments in the Pommerman registry
    print(pommerman.REGISTRY)
    print(ENV_ID)
    # Create a set of agents (exactly four)
    agent_list = [
        #random_agent.SmartRandomAgentNoBomb(),
        simple_agent_cautious_bomb.SimpleAgentNoBombs(),
        simple_agent_cautious_bomb.SimpleAgentNoBombs(),
        agents.simple_agent.SimpleAgent(),
        agents.simple_agent.SimpleAgent(),
    ]
    # Make the "Free-For-All" environment using the agent list
    env = pommerman.make(ENV_ID, agent_list)
    # Run the episodes just like OpenAI Gym
    win_cnt=0; draw_cnt=0; lost_cnt=0
    for i_episode in range(N_game):
        state = env.reset()
        done = False
        step_cnt=0
        while not done:
            if RENDER: env.render()
            actions = env.act(state)
            state, rewards, done, info = env.step(actions)
            step_cnt +=1
        if rewards[0]>0: win_cnt +=1
        elif 'draw' in info: draw_cnt +=1
        else: lost_cnt = lost_cnt + 1
        print('Episode {} finished'.format(i_episode))
    print('win:', win_cnt, 'draw:', draw_cnt, 'lose:', lost_cnt)
    print('\n')
    env.close()

if __name__ == '__main__':
    main()
