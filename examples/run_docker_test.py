'''An example to show how to set up an pommerman game programmatically'''
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import pommerman
from pommerman import agents
from pommerman.agents.nn_agent import NNAgent
from pommerman.agents.model import CNN_LSTM
from pommerman.agents import random_agent
from pommerman.agents import cnn_model
from pommerman.agents import simple_agent_nobombs
from pommerman.agents import simple_agent_cautious_bomb

import torch
import argparse
def main():
    '''Simple function to bootstrap a game.
       
       Use this as an example to set up your training env.
    '''
    # Print all possible environments in the Pommerman registry
    print(pommerman.REGISTRY)
    parser=argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    #parser.add_argument('--env_id', type=str, default='PommeTeamCompetition-v0', help='must be PommeFFACompetition-v0 or PommeTeamCompetition-v0')
    parser.add_argument('--docker0', type=str, default=None, help='docker tag name') 
    parser.add_argument('--docker1', type=str, default=None, help='docker tag name') 
    parser.add_argument('--docker2', type=str, default=None, help='docker tag name') 
    parser.add_argument('--docker3', type=str, default=None, help='docker tag name') 
    parser.add_argument('--n_episode', type=int, default=10, help='how many games to run')
    parser.add_argument('--with_render', action='store_true', default=False, help='render or not?')
    args=parser.parse_args()

    # Create a set of agents (exactly four)
    env_id="PommeTeamCompetition-v0"
    agent_list=[None]*4

    name=args.docker0
    my_docker_agent=agents.docker_agent.DockerAgent(name, port=1234)
    #name="pommerman/2_mesozoic_smart_186"
    name=args.docker2
    my_docker_agent2=agents.docker_agent.DockerAgent(name, port=1235)

    oppo_name=args.docker1
    oppo_docker=agents.docker_agent.DockerAgent(oppo_name, port=2235)
    oppo_name=args.docker3
    oppo_docker2=agents.docker_agent.DockerAgent(oppo_name, port=2236)

    agent_list[0]=my_docker_agent
    agent_list[2]=my_docker_agent2

    agent_list[1]=oppo_docker
    agent_list[3]=oppo_docker2
    
    env = pommerman.make(env_id, agent_list).unwrapped
    print('Env:', env_id, agent_list)
    

    json_dir='./json_logs'
    if not os.path.exists(json_dir):
        os.makedirs(json_dir)
    print('record json dir:', json_dir)
    # Run the episodes just like OpenAI Gym
    win_cnt=0
    draw_cnt=0
    first_team=0
    for i_episode in range(args.n_episode):
        #env.set_init_game_state('/tmp/000.json')
        state = env.reset()
        done = False
        rewards=None
        while not done:
            if args.with_render: 
                env.render(record_json_dir=json_dir)
            actions = env.act(state)
            #print('actions', actions, 'nn alive', neuro_agent.is_alive)
            state, rewards, done, info = env.step(actions)
        print('Episode {} finished'.format(i_episode))
        if rewards[first_team]>0:
            print('0-2 team won')
            win_cnt +=1
        if rewards[first_team]<0 and rewards[(first_team+1)%4]<0:
            draw_cnt +=1
        pommerman.utility.join_json_state(json_dir, ['test','test','test','test'], finished_at=0, config=env_id, info=info)
    print('0-2 team win:', win_cnt, 'draw:', draw_cnt, 'total:', args.n_episode)
    env.close()

if __name__ == '__main__':
    main()
