'''An example to show how to set up an pommerman game programmatically'''
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import pommerman
from pommerman import agents
from pommerman.agents.nn_agent import NNAgent
from pommerman.agents.cnn_model import CNNBatchNorm

import torch

def main():
    '''Simple function to bootstrap a game.
       
       Use this as an example to set up your training env.
    '''
    # Print all possible environments in the Pommerman registry
    print(pommerman.REGISTRY)

    # Create a set of agents (exactly four)    

    shape=(14,11,11)
    n_actions=6
    n_filters_per_layer=64
    n_cnn_layers=4
    nn_model=CNNBatchNorm(input_feature_shape=shape, n_actions=n_actions, n_filters_per_layer=n_filters_per_layer, n_cnn_layers=n_cnn_layers)
    nn_path='./output/NN_MODELS/ppo_CNN4_64_99.pt' #CHANGE THIS to your actual checkpoint file. Currently assumes you are calling the script from main dir
    nn_model.load_state_dict(torch.load(nn_path, map_location=lambda storage, loc: storage))
    selection='softmax'
    nn_agent = NNAgent(nn_model, action_selection=selection, is_training=False)
    nn_agent2 = NNAgent(nn_model, action_selection=selection, is_training=False)
    
    idx=0
    team_id=(idx+2)%4
    #env_id="PommeFFACompetition-v0"
    #env_id="PommeTeamCompetition-v0"
    env_id="SimpleTeam-v0"
    agent_list = [
        agents.RandomAgent(),
        agents.PlayerAgent(),
        agents.RandomAgent(),
        agents.PlayerAgent(),
        #agents.RandomAgent(),
    ]
    agent_list[idx]=nn_agent
    agent_list[team_id]=nn_agent2
    # Make the environment using the agent list
    env = pommerman.make(env_id, agent_list)

    # Run the episodes just like OpenAI Gym
    for i_episode in range(1):
        state = env.reset()
        done = False
        while not done:
            env.render()
            actions = env.act(state)
            #a=nn_agent.act(state[idx], env.action_space, 'softmax') if nn_agent.is_alive else 0
            #actions[idx]=a
            #print('actions', actions, 'nn alive', nn_agent.is_alive)
            state, reward, done, info = env.step(actions)
            #if nn_agent.is_alive ==False: print('dead')
        print('Episode {} finished'.format(i_episode))
        print("Final Result: ", info)
    env.close()


if __name__ == '__main__':
    main()
