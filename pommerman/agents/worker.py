import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))
import itertools
import torch
import numpy as np

import pommerman
from pommerman.agents import nn_agent
from pommerman.agents import simple_agent
from pommerman import constants
from pommerman.agents import input_util2
from pommerman import utility
import random
import copy
import psutil
import pickle 
import glob
from collections import deque
from pommerman.agents.game_buffer import compute_advantage, Transition 
from pommerman.agents import random_agent
from pommerman.agents.cnn_model import CNNBatchNorm

def randomized_start(env, max_n_rigid=constants.NUM_RIGID, max_n_wood=constants.NUM_WOOD, max_n_item=constants.NUM_ITEMS):
    env.seed(os.getpid())
    # rigid: wall, wood: wood, item: powerup
    n_rigid=random.randint(1, max_n_rigid/2)
    n_rigid *=2
    n_wood=random.randint(1, max_n_wood/2)
    n_wood *=2
    n_item=min(max_n_item, random.randint(1, n_wood))
    env._num_rigid=n_rigid
    env._num_wood=n_wood
    env._num_items=n_item
    obs=env.reset()
    return obs


def train_act(agent, observation, env):
    prob, value = 0.0, 0.0
    a=constants.Action.Stop.value
    action_mask=None
    if not agent.is_alive:
        return  a, prob, value, action_mask
    if isinstance(agent, nn_agent.NNAgent):
        agent.set_train_mode(True)
        a, prob, value, action_mask=agent.act(observation, env.action_space)
    else:
        a=agent.act(observation, env.action_space)
    return a, prob, value, action_mask

def play_games(agent_list, env_id, num_games, training_agent_id, gae_n_step, gae_discount, gae_lambda, random_start):
    print('num games:', num_games, "agent_list:", agent_list)
    #play games and compute advantage estimates 
    env = pommerman.make(env_id, agent_list).unwrapped
    env.seed(os.getpid())
    env.set_training_agent(training_agent_id) #training_agent won't act by env.act
    assert(len(agent_list)==4)
    teammate_id=(training_agent_id+2)%4

    game_count=0
    game_list=[]
    position_queue=deque(maxlen=32)
    while game_count < num_games:
        game=[]
        game2=[]
        if random_start:
            print('random start')
            obs=randomized_start(env)
        else:
            print('default start')
            obs = env.reset() #uncomment for default start
        step=0
        position_queue.clear()
        prev_is_alive=True
        prev_is_alive_teammate=True
        while True:
            train_agent=agent_list[training_agent_id]
            assert(train_agent.agent_id == training_agent_id)
            actions=[]
            probs=[]
            values=[]
            action_masks=[]
            prev_is_alive, prev_is_alive_teammate=train_agent.is_alive, agent_list[teammate_id].is_alive 
            for i, agent in enumerate(agent_list):
                a, prob, value, action_mask=train_act(agent, obs[i], env)
                actions.append(a) 
                probs.append(prob)
                values.append(value)
                action_masks.append(action_mask)
            assert(len(actions) == len(agent_list))

            copy_obs=copy.deepcopy(obs)
            #env.render() #uncomment to see runs. May need to modify RENDER_FPS for your environment (in configs.py)
            obs_prime, rewards, done, info=env.step(actions)
            intermediate_rewards=input_util2.get_intermediate_rewards(copy_obs, obs_prime, position_queue)
            del copy_obs
            if not done:
                rewards= intermediate_rewards
            if done and step>constants.MAX_STEPS:
                print('Draw rewards:', rewards)
                for i, agent in enumerate(agent_list):
                    if agent.is_alive:
                        #rewards[i] = rewards[i]/2
                        rewards[i] = -1.0
                    else:
                        rewards[i] = -1.0
                print('modified draw rewards:', rewards)
            if prev_is_alive: 
                a, reward, prob, value = actions[training_agent_id], rewards[training_agent_id], probs[training_agent_id], values[training_agent_id]
                state=train_agent.my_state
                action_mask=action_masks[training_agent_id]
                if not train_agent.is_alive:
                    reward = -1.0 #this agent is dead at this step
                trans=Transition(state=state, action=a, reward=reward, value_of_state=value, prob_of_action=prob, cumulative_return=0.0, action_mask=action_mask) 
                game.append(trans)
            if prev_is_alive_teammate:
                a, reward, prob, value = actions[teammate_id], rewards[teammate_id], probs[teammate_id], values[teammate_id]
                state=agent_list[teammate_id].my_state
                action_mask=action_masks[teammate_id]
                if not agent_list[teammate_id].is_alive:
                    reward = -1.0 #this agent is dead at this step
                trans=Transition(state=state, action=a, reward=reward, value_of_state=value, prob_of_action=prob, cumulative_return=0.0, action_mask=action_mask) 
                game2.append(trans)
            obs = obs_prime
            step += 1
            if done:
                print('pid:', os.getpid(), 'finished one episode with rewards', rewards, 'step:', step)
                break

        if step<=constants.MAX_STEPS and ((not train_agent.is_alive and agent_list[teammate_id].is_alive) or (train_agent.is_alive and not agent_list[teammate_id].is_alive )):
            trans=game[-1]
            s1,a1,r1,v1,p1=trans.state, trans.action, trans.reward,trans.value_of_state,trans.prob_of_action
            action_mask1=trans.action_mask
            if not train_agent.is_alive:
                r1=-0.5 # teammate survives, so train_agent get non -1.0 even though not alive
                assert(agent_list[teammate_id].is_alive)
                r2=0.6
            trans=game2[-1]
            s2,a2,r2,v2,p2=trans.state, trans.action, trans.reward,trans.value_of_state,trans.prob_of_action
            action_mask2=trans.action_mask
            if not agent_list[teammate_id].is_alive:
                r2=-0.5 # not -1.0 even though not alive
                assert(train_agent.is_alive)
                r1=0.6
            game[-1]=Transition(state=s1, action=a1, reward=r1, value_of_state=v1, prob_of_action=p1, cumulative_return=0.0, action_mask=action_mask1)
            game2[-1]=Transition(state=s2, action=a2, reward=r2, value_of_state=v2, prob_of_action=p2, cumulative_return=0.0, action_mask=action_mask2)
        #compute advantage
        game=compute_advantage(game, gae_n_step, gae_discount, gae_lambda)
        game2=compute_advantage(game2, gae_n_step, gae_discount, gae_lambda)
        game_list.append(game)
        game_list.append(game2)
        game_count += 1
    process = psutil.Process(os.getpid())
    print('RSS memory (GB) %.3f, process id %d'%(process.memory_info().rss/(10**9), os.getpid()))
    print('process:', os.getpid(), 'terminates.')
    env.close()
    return game_list

def save_game_list(game_list, gamedir, suffix='.game_list'):
    pid=os.getpid()
    destpath=os.path.join(gamedir, repr(pid)+suffix)
    with open(destpath, 'wb') as f:
        pickle.dump(game_list, f)

def load_newest_nn(nn_model_dir, input_shape, n_actions, n_filters_per_layer, n_cnn_layers, device_id=None, nn_type='CNN'):    
    if nn_type == 'CNN':
        nn_model=CNNBatchNorm(input_shape, n_actions, n_filters_per_layer, n_cnn_layers)
    else: 
        nn_model=pommerman.agents.model.CNN_LSTM(input_shape, n_actions, n_filters_per_layer, n_cnn_layers)
    if device_id is not None:
        nn_model.cuda(device_id)
    list_of_files = glob.glob(os.path.join(nn_model_dir, '*.pt')) # * means all if need specific format then *.csv
    latest_nn = max(list_of_files, key=os.path.getctime) if len(list_of_files)>0 else None
    if latest_nn is not None: 
        print('load nn:', latest_nn)
        nn_model.load_state_dict(torch.load(latest_nn, map_location=lambda storage, loc: storage))
        #nn_model.load_state_dict(torch.load(latest_nn))
    return nn_model

def setup_agents(nn_model, max_seq_len, opponent='static'):
    agent_list=[None]*4
    train_agent_id=random.randint(0,3)
    agent_list[train_agent_id]=nn_agent.NNAgent(nn_model, is_training=True, max_seq_len=max_seq_len)
    team_id=(train_agent_id+2)%4
    for i in range(4):
        if i == train_agent_id: 
            continue
        if i == team_id:
            agent_list[i]=nn_agent.NNAgent(nn_model, is_training=True, max_seq_len=max_seq_len)
        else: 
            if opponent == 'static':
                agent_list[i] = random_agent.StaticAgent()
            elif opponent == 'slow_random_no_bomb':
                agent_list[i] = random_agent.SlowRandomAgentNoBomb()
            elif opponent == 'timed_random_no_bomb':
                agent_list[i] = random_agent.TimedRandomAgentNoBomb()
            elif opponent == 'smart_random_no_bomb':
                agent_list[i] = random_agent.SmartRandomAgentNoBomb()
            elif opponent == 'smart_random':
                agent_list[i] = random_agent.SmartRandomAgent()
            elif opponent == 'simple_agent':
                agent_list[i]=simple_agent.SimpleAgent() 
            elif opponent == 'nn_agent':
                agent_list[i]=nn_agent.NNAgent(nn_model, max_seq_len=max_seq_len)
            else:
                print('unsupported opponent type!')
                sys.exit(1)

    return train_agent_id, agent_list

def produce_games(params, save_games=True):
    gae_n_step, gae_discount, gae_lambda = params['gae_n_step'], params['gae_discount'], params['gae_lambda']
    nn_model_dir, game_dir = params['nn_model_dir'], params['game_dir']
    input_shape, n_actions, n_filters_per_layer, n_cnn_layers=params['input_shape'], params['n_actions'], params['n_filters_per_layer'], params['n_cnn_layers']
    env_id=params['env_id']
    n_games=params['n_games_per_worker']
    device_id=params['device_id']
    opponent=params['opponent']

    nn_model=load_newest_nn(nn_model_dir, input_shape, n_actions, n_filters_per_layer, n_cnn_layers, device_id, params['nn_type'])

    train_id, agent_list=setup_agents(nn_model, params['chunk_size'], opponent)
    random_start=params['random_start']
    #play games and compute_advantage
    game_list=play_games(agent_list, env_id, n_games, train_id, gae_n_step, gae_discount, gae_lambda, random_start)
    #save games to game_dir
    if save_games:
        save_game_list(game_list, game_dir)
    print('---WORKER process %d has finished---'%os.getpid())
    if not save_games:
        return game_list


if __name__ == "__main__":
    '''Run this worker directly for playing and storing games '''
    import argparse
    parser=argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--n_workers', type=int, default=2, help='number of worker threads')
    parser.add_argument('--n_games_per_worker', type=int, default=10, help='number of games per work') 
    parser.add_argument('--batch_seq_size', type=int, default=32, help='mini-batch size games per training sample')
    parser.add_argument('--chunk_size', type=int, default=128, help='chunk size when split a long seq into chunks')
    parser.add_argument('--buffer_size', type=int, default=100, help='number of games in the buffer')
    parser.add_argument('--env_id', type=str, default='PommeTeamCompetition-v0', help="environment id string. Possible values: [PommeFFACompetition-v0, PommeFFACompetitionFast-v0, PommeFFAFast-v0, PommeFFA-v1, PommeRadio-v2, PommeTeamCompetition-v0, PommeTeam-v0, PommeTeamFast-v0] ")
    parser.add_argument('--objective', type=str, default='ppo', help='should be one of {maximum_likelihood, a2c, ppo}')
    parser.add_argument('--max_loop_step', type=int, default=10, help='maximum training steps')
    parser.add_argument('--game_dir', type=str, default="GAMES", help='log dir')
    parser.add_argument('--nn_model_dir', type=str, default="NN_MODELS", help='log dir')
    parser.add_argument('--opponent', type=str, default='static', help='must be one of {static, random, slow_random_no_bomb, smart_random, smart_random_no_bomb}')

    parser.add_argument('--n_epochs', type=int, default=1, help='how many epochs to train given a set of games in game_memory')
    parser.add_argument('--optimizer', type=str, default='adam', help='which optimizer to use {momentum, adam}')
    parser.add_argument('--gae_discount', type=float, default=0.998, help='reward discount rate')
    parser.add_argument('--gae_lambda', type=float, default=0.95, help='lambda for Generalized Advantage Estimate (weighting factor, 0 then one step TD, 1 T-step)')
    parser.add_argument('--gae_n_step', type=int, default=256, help='for Generalized Advantage Estimate, how many steps lookahead')
    parser.add_argument('--entropy_loss_coeff', type=float, default=0.01,  help='entropy loss weight')
    
    parser.add_argument('--learning_rate', type=float, default=0.001, help='learning rate')
    parser.add_argument('--input_shape', type=tuple, default=(14,11,11), help='input shape for CNN-LSTM')
    parser.add_argument('--n_actions', type=int, default=6, help='there are 6 actions for pommerman')
    parser.add_argument('--n_cnn_layers', type=int, default=4, help='how deep is the CNN')
    parser.add_argument('--n_filters_per_layer', type=int, default=64, help='how many 3x3 filters per layer')
    parser.add_argument('--device_id', type=int, default=None, help='on which device, cup or cuda:0 or cuda:1 or ..')
    parser.add_argument('--random_start', type=bool, default=False, help='random start state')
    parser.add_argument('--nn_type', type=str, default='CNN', help='CNN or CNN_LSTM')

    args=parser.parse_args()
    params=vars(args)
    produce_games(params)
