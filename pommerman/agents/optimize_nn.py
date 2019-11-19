"""Trains a neural network given set of collected playouts of a policy.
"""

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))
import itertools
import torch
import numpy as np
import torch.multiprocessing as mp

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

import glob
from pommerman.agents.game_buffer import GameBuffer
from pommerman.agents.game_buffer import split_to_chunks
from pommerman.agents import worker

def read_games_to_buffer(buffer_size, gamedir, suffix='.game_list'):
    gameBuffer=GameBuffer(capacity=buffer_size)
    list_files=glob.glob(os.path.join(gamedir, "*"+suffix))
    list_files.sort(key=os.path.getctime, reverse=True)
    for filename in list_files:
        game_list_file_path = filename
        if os.path.isfile(game_list_file_path) and game_list_file_path.endswith(suffix):
            opened_file=open(game_list_file_path,'rb')
            game_list=pickle.load(opened_file)
            print('game_list len:', len(game_list))
            opened_file.close()
            for g in game_list:
                gameBuffer.push(g)
            print('removing:', game_list_file_path)
            os.system('rm '+ game_list_file_path)
            if buffer_size == len(gameBuffer): 
                print('buffer is full')
                break
    assert(len(gameBuffer) == buffer_size)
    return gameBuffer

def optimize_nn(params, iteration, nn_model=None, optimizer=None, gameBuffer=None):
    buffer_size=params['buffer_size']
    game_dir=params['game_dir']
    if gameBuffer==None:
        gameBuffer=read_games_to_buffer(buffer_size, game_dir)

    nn_model_dir=params['nn_model_dir']

    input_shape=params['input_shape']
    n_actions=params['n_actions']
    n_filters_per_layer=params['n_filters_per_layer']
    n_cnn_layers=params['n_cnn_layers']
    if not nn_model:
        nn_model=worker.load_newest_nn(nn_model_dir, input_shape, n_actions, n_filters_per_layer, n_cnn_layers, 'cuda:0', params['nn_type'])

    learning_rate=params['learning_rate']
    if not optimizer:
        optimizer=torch.optim.Adam(nn_model.parameters(), lr=learning_rate, eps=1e-5) if params['optimizer'] == 'adam' else torch.optim.SGD(nn_model.parameters(), lr=learning_rate, momentum=0.9)
    print('optimizer:', optimizer)

    batch_seq_size=params['batch_seq_size']
    num_epochs=params['n_epochs']
    chunk_size=params['chunk_size']
    objective=params['objective']

    policy_loss_coeff=params['policy_loss_coeff']
    value_loss_coeff=params['value_loss_coeff']
    entropy_coeff=params['entropy_loss_coeff']

    print('training by %s, batch_seq_size:%d, game buffer size:%d, training for %d epochs'%(objective, batch_seq_size, len(gameBuffer), num_epochs))
    print(params)

    #nn_model=torch.nn.DataParallel(nn_model)
    #nn_model.cuda()
    nn_model.train()
    steps_per_epoch=max(len(gameBuffer)//batch_seq_size,1)
    n_steps=num_epochs*steps_per_epoch
    total_loss=0.0
    step=0
    epoch_cnt=0
    epoch_loss=0.0
    step2=0

    while step < n_steps:
        optimizer.zero_grad()
        batch_s, batch_a, batch_A_s, batch_value_of_state, batch_prob_of_action, batch_R, batch_action_mask = gameBuffer.sample(batch_seq_size)
        device=next(nn_model.parameters()).device
        batch_p_logits, batch_v_logit = nn_model(torch.tensor(batch_s).to(device).float())

        batch_a=torch.tensor(batch_a).long().to(device)
        batch_A_s=torch.tensor(batch_A_s).float().to(device)
        batch_value_of_state=torch.tensor(batch_value_of_state).float().to(device)
        batch_prob_of_action=torch.tensor(batch_prob_of_action).float().to(device)
        batch_R=torch.tensor(batch_R).float().to(device)
        batch_action_mask=torch.tensor(batch_action_mask).to(device)
        loss=nn_model.compute_loss(batch_p_logits, batch_v_logit, batch_a, batch_A_s, batch_value_of_state, batch_prob_of_action,batch_R, \
                batch_action_mask,p_coeff=policy_loss_coeff, entropy_coeff=entropy_coeff,v_coeff=value_loss_coeff)

        total_loss += loss.item()
        epoch_loss += loss.item()
        loss.backward()
        print('train step:', step, 'loss ', loss.item())
        if (step+1)%steps_per_epoch == 0:
            print('epoch %d finished'%(epoch_cnt))
            print('epoch average loss', epoch_loss/(step-step2))
            step2=step
            epoch_loss=0.0
            epoch_cnt +=1
        torch.nn.utils.clip_grad_norm_(nn_model.parameters(), max_norm=0.5)
        optimizer.step()
        step += 1
        del batch_p_logits, batch_v_logit, loss
    print('Average loss: ', total_loss/n_steps)

    save_nn(nn_model, nn_model_dir, prefix=objective+'_'+params['nn_type'], suffix=repr(iteration))

def save_nn(nn_model, destdir, prefix, suffix):
    save_name= prefix+repr(nn_model.n_layers) + "_"+ repr(nn_model.n_filters) + "_" + suffix + ".pt"
    torch.save(nn_model.state_dict(), os.path.join(destdir, save_name))

if __name__ == "__main__":
    import argparse
    parser=argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--n_workers', type=int, default=2, help='number of worker threads')
    parser.add_argument('--n_games_per_worker', type=int, default=10, help='number of games per work') 
    parser.add_argument('--batch_seq_size', type=int, default=4, help='mini-batch size games per training sample')
    parser.add_argument('--buffer_size', type=int, default=100, help='number of games in the buffer')
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
    parser.add_argument('--gae_n_step', type=int, default=256, help='for Generalized Advantage Estimate, how many steps lookahead')
    parser.add_argument('--entropy_loss_coeff', type=float, default=0.01,  help='entropy loss weight')
    parser.add_argument('--policy_loss_coeff', type=float, default=1.0,  help='entropy loss weight')
    parser.add_argument('--value_loss_coeff', type=float, default=0.5,  help='entropy loss weight')

    
    parser.add_argument('--learning_rate', type=float, default=0.001, help='learning rate')
    parser.add_argument('--input_shape', type=tuple, default=(14,11,11), help='input shape for CNN-LSTM')
    parser.add_argument('--n_actions', type=int, default=6, help='there are 6 actions for pommerman')
    parser.add_argument('--n_cnn_layers', type=int, default=4, help='how deep is the CNN')
    parser.add_argument('--n_filters_per_layer', type=int, default=64, help='how many 3x3 filters per layer')
    parser.add_argument('--device_id', type=int, default=None, help='on which device, cup or cuda:0 or cuda:1 or ..')

    parser.add_argument('--nn_type', type=str, default='CNN', help='CNN or CNN_LSTM')
    parser.add_argument('--random_start', type=bool, default=False, help='random start state')
    parser.add_argument('--iteration', type=int, default=None, help='which loop iteration is this?')
    args=parser.parse_args()
    if args.objective != 'maximum_likelihood' and args.iteration is None:
        print('ppo or a2c requires --iteration not None')
        sys.exit(1)

    params=vars(args)
    optimize_nn(params, args.iteration)
