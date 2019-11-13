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
    parser.add_argument('--n_cnn_layer', type=int, default=4, help='num of cnn layers of the model to load')
    parser.add_argument('--n_filters_per_layer', type=int, default=64, help='num of 3x3 filters per cnn layer')
    parser.add_argument('--input_shape', type=tuple, default=(14,11,11), help='input feature plane shape')
    parser.add_argument('--n_actions', type=int, default=6, help='num of actions')
    parser.add_argument('--env_id', type=str, default='PommeTeamCompetition-v0', help='must be PommeFFACompetition-v0 or PommeTeamCompetition-v0')
    parser.add_argument('--nn_agent_id', type=int, default=0, help='which agent is nn?')
    parser.add_argument('--nn_action_selection', type=str, default='softmax', help='softmax or greedy?')
    parser.add_argument('--nn_path',  type=str, default=None, help='path to nn model')
    parser.add_argument('--n_episode', type=int, default=10, help='how many games to run')
    parser.add_argument('--with_render', action='store_true', default=False, help='render or not?')
    parser.add_argument('--opponent', type=str, default='static', help='static or smart_random or smart_random_no_bomb or simple_agent')
    parser.add_argument('--nn_type', type=str, default='CNN', help='CNN or CNN_LSTM')
    args=parser.parse_args()
    n_layer=args.n_cnn_layer
    n_filter=args.n_filters_per_layer
    shape=args.input_shape
    n_actions=args.n_actions
    env_id=args.env_id
    nn_agent_id=args.nn_agent_id
    nn_path=args.nn_path

    opponent=args.opponent

    # Create a set of agents (exactly four)
    if args.nn_type=='CNN':
        nn_model=cnn_model.CNNBatchNorm(input_feature_shape=shape, n_actions=n_actions, n_filters_per_layer=n_filter, n_cnn_layers=n_layer)
    else:
        nn_model=pommerman.agents.model.CNN_LSTM(input_feature_shape=shape, n_actions=n_actions, n_filters_per_layer=n_filter, n_cnn_layers=n_layer)

    if nn_path is not None: 
        nn_model.load_state_dict(torch.load(nn_path, map_location=lambda storage, loc: storage))
    else:
        print('no nn model to load, so neural net has random weights!')
    # torch.load('my_file.pt', map_location=lambda storage, loc: storage) #for map CUDA pt to CPU

    selection=args.nn_action_selection
    neuro_agent = NNAgent(nn_model, action_selection=selection, is_training=False)
    diag_agent = NNAgent(nn_model, action_selection=selection, is_training=False) if 'Team' in env_id else agents.SimpleAgent()
    diag_id=(nn_agent_id+2)%4
    #env_id="PommeFFACompetition-v0"
    agent_list=[None]*4

    #name="pommerman/mesozoic_smart_186"
    #my_docker_agent=agents.docker_agent.DockerAgent(name, port=1234)
    #name="pommerman/2_mesozoic_smart_186"
    #my_docker_agent2=agents.docker_agent.DockerAgent(name, port=1235)

    #oppo_name="pommerman/deepdrl"
    #oppo_name="pommerman/central_critic"
    #oppo_name="pommerman/psr2"
    #oppo_docker=agents.docker_agent.DockerAgent(oppo_name, port=2235)
    #oppo_docker2=agents.docker_agent.DockerAgent(oppo_name, port=2236)
    
    for i in range(4):
        if i == nn_agent_id: 
            agent_list[i]=neuro_agent
            #agent_list[i]=agents.SimpleAgent()
            #agent_list[i]=my_docker_agent
        elif i == diag_id:
            agent_list[i]=diag_agent
            #agent_list[i]=agents.SimpleAgent()
            #agent_list[i]=my_docker_agent2
        else:
            if opponent == 'static':
                agent_list[i]=random_agent.StaticAgent()
            elif opponent == 'smart_random':
                agent_list[i]=random_agent.SmartRandomAgent()
            elif opponent == 'smart_random_no_bomb':
                agent_list[i]=random_agent.SmartRandomAgentNoBomb()
            elif opponent == 'simple_agent':
                agent_list[i]=agents.SimpleAgent()
            elif opponent == 'simple_agent_no_bomb':
                agent_list[i]=simple_agent_nobombs.SimpleAgentNoBombs()
            elif opponent == 'simple_agent_cautious_bomb':
                agent_list[i]=simple_agent_cautious_bomb.SimpleAgentNoBombs()
            elif opponent == 'docker':
                agent_list[i]=oppo_docker if (i==0 or i==1) else oppo_docker2
            else:
                print('not supported opponent!')
    env = pommerman.make(env_id, agent_list).unwrapped
    print('----Make sure your loaded nn model is the same as your command parameter ---')
    print('loaded', nn_path)
    print('Env:', env_id, agent_list)
    

    json_dir='./json_logs'
    if not os.path.exists(json_dir):
        os.makedirs(json_dir)
    print('record json dir:', json_dir)
    # Run the episodes just like OpenAI Gym
    win_cnt=0
    draw_cnt=0
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
        if rewards[nn_agent_id]>0:
            win_cnt +=1
        if rewards[nn_agent_id]<0 and rewards[(nn_agent_id+1)%4]<0:
            draw_cnt +=1
        pommerman.utility.join_json_state(json_dir, ['test','test','test','test'], finished_at=0, config=env_id, info=info)
    print('win:', win_cnt, 'draw:', draw_cnt, 'total:', args.n_episode)
    env.close()

if __name__ == '__main__':
    main()
