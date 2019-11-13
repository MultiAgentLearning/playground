import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))
import itertools
import torch
import numpy as np
#import torch.multiprocessing as mp
import multiprocessing as mp

import pommerman
from pommerman.agents import nn_agent
from pommerman import constants
from pommerman.agents import input_util2
from pommerman import utility
import random
import copy

import psutil
import pickle 
from collections import deque

from pommerman.agents import worker
from pommerman.agents import optimize_nn
from pommerman.agents import game_buffer

def main(params):
    """
    #The training loop
    #1. play a set of games using multiple worker
    #2. load games, optimize nn
    #3. go back to step 1 
    """
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print('Device:', device)
    mp.set_start_method('spawn')
    learning_rate=params['learning_rate']

    print('algo: %s'%(params['objective']), 'objective:', params['objective'])
    print('games dir:', params['game_dir'], 'nn model save at:', params['nn_model_dir'])
    loop_step=0
    nn_model_dir=params['nn_model_dir']

    input_shape=params['input_shape']
    n_actions=params['n_actions']
    n_filters_per_layer=params['n_filters_per_layer']
    n_cnn_layers=params['n_cnn_layers']
    nn_model=worker.load_newest_nn(nn_model_dir, input_shape, n_actions, n_filters_per_layer, n_cnn_layers, 0, params['nn_type'])
    optimizer=torch.optim.Adam(nn_model.parameters(), lr=params['learning_rate'], eps=1e-5) if params['optimizer'] == 'adam' else torch.optim.SGD(nn_model.parameters(), lr=learning_rate, momentum=0.9)
    while loop_step < params['max_loop_step']:
        pool=mp.Pool(processes=params['n_workers'])
        process = psutil.Process(os.getpid())
        print('Main RSS(GB):', process.memory_info().rss/(10**9))
        print('playing games')
        results=[]
        gpu_count=torch.cuda.device_count()
        
        gameBuffer=game_buffer.GameBuffer(capacity=params['buffer_size'])
        #assign workers to each GPU evenly
        for i in range(params['n_workers']):
            k=i%gpu_count
            #if k not in assign: assign[k]=0
            #else: assign[k] +=1
            #device_string="cuda:"+repr(k) if assign[k]<=3 else 'cpu'
            device_id=k
            #device_string='cpu'
            params2=dict(params)
            print('worker %d on device_id %d'%(i,device_id))
            params2['device_id']=device_id
            results.append(pool.apply_async(worker.produce_games, [params2, False]))

        for i in range(params['n_workers']):
            game_list=results[i].get()
            for g in game_list:
                gameBuffer.push(g)
            del game_list
        print('All workers finished!')
        print('optimize nn')
        optimize_nn.optimize_nn(params, loop_step, nn_model, optimizer,gameBuffer)
        del gameBuffer
        loop_step +=1
        pool.close()
        pool.join()
        del pool

if __name__ == "__main__":
    import argparse
    parser=argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--n_workers', type=int, default=2, help='number of worker threads')
    parser.add_argument('--n_games_per_worker', type=int, default=10, help='number of games per work') 
    parser.add_argument('--batch_seq_size', type=int, default=4, help='mini-batch size games per training sample')
    parser.add_argument('--buffer_size', type=int, default=20, help='number of games in the buffer')
    parser.add_argument('--env_id', type=str, default='PommeTeamCompetition-v0', help="environment id string. Possible values: [PommeFFACompetition-v0, PommeFFACompetitionFast-v0, PommeFFAFast-v0, PommeFFA-v1, PommeRadio-v2, PommeTeamCompetition-v0, PommeTeam-v0, PommeTeamFast-v0] ")
    parser.add_argument('--objective', type=str, default='ppo', help='should be one of {maximum_likelihood, a2c, ppo}')
    parser.add_argument('--max_loop_step', type=int, default=10, help='maximum training steps')
    parser.add_argument('--game_dir', type=str, default="GAMES", help='log dir')
    parser.add_argument('--nn_model_dir', type=str, default="NN_MODELS", help='log dir')

    parser.add_argument('--opponent', type=str, default='static', help='must be one of {static, random, smart_random, smart_random_no_bomb}')

    parser.add_argument('--chunk_size', type=int, default=12, help='chunk size when split a long seq into chunks')

    parser.add_argument('--n_epochs', type=int, default=1, help='how many epochs to train given a set of games in game_memory')
    parser.add_argument('--optimizer', type=str, default='adam', help='which optimizer to use {momentum, adam}')
    parser.add_argument('--gae_discount', type=float, default=0.998, help='reward discount rate')
    parser.add_argument('--gae_lambda', type=float, default=0.95, help='lambda for Generalized Advantage Estimate (weighting factor, 0 then one step TD, 1 T-step)')
    parser.add_argument('--gae_n_step', type=int, default=2560, help='for Generalized Advantage Estimate, how many steps lookahead')
    parser.add_argument('--entropy_loss_coeff', type=float, default=0.01,  help='entropy loss weight')
    parser.add_argument('--policy_loss_coeff', type=float, default=1.0,  help='entropy loss weight')
    parser.add_argument('--value_loss_coeff', type=float, default=0.5,  help='entropy loss weight')
    
    parser.add_argument('--learning_rate', type=float, default=0.0003, help='learning rate')
    parser.add_argument('--input_shape', type=tuple, default=(14,11,11), help='input shape for neuralnet')
    parser.add_argument('--n_actions', type=int, default=6, help='there are 6 actions for pommerman')
    parser.add_argument('--n_cnn_layers', type=int, default=4, help='how deep is the CNN')
    parser.add_argument('--n_filters_per_layer', type=int, default=64, help='how many 3x3 filters per layer')
    parser.add_argument('--device_id', type=int, default=None, help='on which device, cup or cuda:0 or cuda:1 or ..')
    parser.add_argument('--random_start', type=bool, default=False, help='random start state')
    parser.add_argument('--nn_type', type=str, default='CNN', help='CNN or CNN_LSTM')

    args=parser.parse_args()
    params=vars(args)
    main(params)
