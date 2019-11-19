'''An example to show how to set up an pommerman game programmatically'''
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import pommerman
from pommerman import agents
from pommerman.agents.nn_agent import NNAgent
from pommerman.agents.model import CNN_LSTM

import torch

def main():
    '''Simple function to bootstrap a game.
       
       Use this as an example to set up your training env.
    '''
    # Print all possible environments in the Pommerman registry
    print(pommerman.REGISTRY)

    # Create a set of agents (exactly four)
    lstm_nn_model = CNN_LSTM(input_feature_shape=(9,11,11), n_actions=6, 
            n_filters_per_layer=64, n_cnn_layers=6)
    lstm_nn_model.load_state_dict(torch.load('/home/cgao3/pommerman/pommerman/agents/LOGS/ppo_cnn_lstm_cnn_6_64_27.pt', map_location=lambda storage, loc: storage))
# torch.load('my_file.pt', map_location=lambda storage, loc: storage) #for map CUDA pt to CPU

    nn_agent = NNAgent(lstm_nn_model)
    nn_agent2 = NNAgent(lstm_nn_model)
    idx=0
    team_id=(idx+2)%4
    #env_id="PommeFFACompetition-v0"
    env_id="PommeTeamCompetition-v0"
    agent_list = [
#nn_agent,
        agents.RandomAgent(),
        agents.SimpleAgent(),
        agents.RandomAgent(),
        #agents.SimpleAgent(),
        agents.RandomAgent(),
        # agents.DockerAgent("pommerman/simple-agent", port=12345),
    ]
    agent_list[idx]=nn_agent
    agent_list[team_id]=nn_agent2
    # Make the "Free-For-All" environment using the agent list
    env = pommerman.make(env_id, agent_list)

    # Run the episodes just like OpenAI Gym
    for i_episode in range(20):
        state = env.reset()
        done = False
        while not done:
            #env.render()
            actions = env.act(state)
            #a=nn_agent.act(state[idx], env.action_space, 'softmax') if nn_agent.is_alive else 0
            #actions[idx]=a
            print('actions', actions, 'nn alive', nn_agent.is_alive)
            state, reward, done, info = env.step(actions)
            #if nn_agent.is_alive ==False: print('dead')
        print('Episode {} finished'.format(i_episode))
    env.close()


if __name__ == '__main__':
    main()
