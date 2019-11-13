"""Implementation of a simple deterministic agent using Docker."""
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from pommerman import agents
from pommerman.runner import DockerAgentRunner

from pommerman.agents.nn_agent import NNAgent
from pommerman.agents import random_agent
from pommerman.agents import cnn_model
from pommerman.agents import simple_agent_nobombs
import torch


class MyAgent(DockerAgentRunner):
    '''An example Docker agent class'''

    def __init__(self):
        super(MyAgent, self).__init__()
        #self._agent = agents.SimpleAgent()
        shape=(14,11,11)
        n_actions=6
        n_filters_per_layer=64
        n_cnn_layers=4
        nn_model=cnn_model.CNNBatchNorm(input_feature_shape=shape, n_actions=n_actions, n_filters_per_layer=n_filters_per_layer, n_cnn_layers=n_cnn_layers)
        #nn_path='./nips_nn_mesozoic_smart/ppo_CNN4_64_1915.pt'
        nn_path='./skynet_smart/ppo_CNN4_64_955.pt'
        nn_model.load_state_dict(torch.load(nn_path, map_location=lambda storage, loc: storage))
        selection='softmax'
        neuro_agent = NNAgent(nn_model, action_selection=selection, is_training=False)
        self._agent=neuro_agent

    def act(self, observation, action_space): 
        return self._agent.act(observation, action_space) 
    
    def init_agent(self, id, game_type): 
        return self._agent.init_agent(id, game_type) 

    def episode_end(self, reward):
        return self._agent.episode_end(reward) 

    def shutdown(self): 
        return self._agent.shutdown() 

def main():
    '''Inits and runs a Docker Agent'''
    agent = MyAgent()
    agent.run()


if __name__ == "__main__":
    main()
