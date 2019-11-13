from pommerman.agents import input_util2
from pommerman.agents import filter_action
from pommerman.agents.base_agent import BaseAgent
import pommerman.characters

import numpy as np
import pommerman.agents.model
from pommerman.agents import cnn_model
import torch
import torch.nn.functional as F
from collections import deque
import time

class NNAgent(BaseAgent):
    """
    common neural net agent using LSTM
    @author Chao Gao, cgao3@ualberta.ca
    """
    def __init__(self, nn_model, action_selection='softmax', is_training=False, max_seq_len=12,
            character=pommerman.characters.Bomber):
        super(NNAgent, self).__init__()
        #only keep most recent max_seq_len observations
        self.seq_state=deque(maxlen=max_seq_len)
        self.k_episode=0
        self.name='neural_net_agent'
        self.nn_model=nn_model

        self.is_training=is_training
        self.action_selection=action_selection
        self.max_seq_len=max_seq_len
        self.total_step=0

        self.retrospect_init_flag=False
        self.retrospect_board=None
        self.retrospect_bomb_life=None
        self.retrospect_bomb_blast_strength=None
        self.my_state=None
    
    def set_train_mode(self, flag):
        self.is_training=flag

    def act(self, observation, action_space):
        if len(self.seq_state) == self.max_seq_len:
            self.seq_state.clear()
        start_time=time.time()
        assert(self.is_alive)
        (i,j)=observation['position']
        board=observation['board']
        self.agent_id_on_board = board[i][j]
        assert(self.agent_id_on_board!=0)

        if self.retrospect_init_flag == False:
            self.retrospect_init_flag=True
            self.retrospect_board=np.copy(observation['board'])
            sz=len(observation['board'])
            self.retrospect_board[(1,1)]=pommerman.constants.Item.Agent0.value
            self.retrospect_board[(sz-2,1)]=pommerman.constants.Item.Agent1.value
            self.retrospect_board[(sz-2,sz-2)]=pommerman.constants.Item.Agent2.value
            self.retrospect_board[(1,sz-2)]=pommerman.constants.Item.Agent3.value
            self.retrospect_bomb_life=np.copy(observation['bomb_life'])
            self.retrospect_bomb_blast_strength=np.copy(observation['bomb_blast_strength'])

        featurized_state = pommerman.agents.input_util2.make_featurize_planes(observation, self.total_step,\
                self.retrospect_board, self.retrospect_bomb_life, self.retrospect_bomb_blast_strength)
        self.my_state=featurized_state 
        self.seq_state.append(featurized_state)
        valid_actions=filter_action.get_filtered_actions(observation)

        action_mask=np.ndarray(shape=(self.nn_model.n_actions,), dtype=np.int16)
        action_mask.fill(0)
        for i in valid_actions:
            action_mask[i]=1
         
        action, prob_of_action, value_of_state = self.sample(valid_actions, action_mask)
        self.total_step +=1
        #print(self.name,  pommerman.constants.Action(action))
        #print('time cost per move: %s seconds'%(time.time()-start_time))
        if self.is_training:
            return action, prob_of_action, value_of_state, action_mask
        else:
            return action
    
    def sample(self, valid_actions, action_mask):
        self.nn_model.eval()
        assert(self.action_selection in ['greedy', 'softmax'])
        with torch.no_grad():
            if isinstance(self.nn_model, pommerman.agents.model.CNN_LSTM):
                batch_seq=[list(self.seq_state)]
                p_logits,v_logit=self.nn_model(self.seq_state)
            else:
                assert(isinstance(self.nn_model, pommerman.agents.cnn_model.CNNBatchNorm))
                batch=torch.tensor([np.float32(self.my_state)])
                batch=batch.to(next(self.nn_model.parameters()).device)
                p_logits,v_logit=self.nn_model(batch)
            p_logits=p_logits.detach()
            v_logit=v_logit.detach()
            value=torch.tanh(v_logit[-1]).item()

            probsTensor=cnn_model.masked_softmax(p_logits, torch.tensor([action_mask]).to(next(self.nn_model.parameters()).device))
            probs=probsTensor[-1].cpu().numpy()
            probs=probs*np.array(action_mask)
            probs=probs/sum(probs)

            #valid_logit_actions=[(a,logit) for a,logit in enumerate(p_logits[-1]) if a in valid_actions]
            #valid_logits=torch.Tensor([logit for a,logit in valid_logit_actions])
            #valid_probs=F.softmax(valid_logits, dim=0)

            #prob_action_list=[(valid_probs[i], a) for i,(a,logit) in enumerate(valid_logit_actions)]
            #prob, action=max(prob_action_list, key=lambda e: e[0])
            prob, action=max(probs), np.argmax(probs)
            del probsTensor, v_logit, p_logits
            if self.action_selection == 'greedy':
                return action, prob, value
            elif self.action_selection =='softmax':
                assert(len(valid_actions) > 0)
                #multi_nomial=torch.distributions.Categorical(logits=valid_logits)
                #i=multi_nomial.sample().item()
                #action=valid_logit_actions[i][0]
                #prob=probs[action]
                #prob=valid_probs[i].item()
                action=np.random.choice([i for i in range(len(action_mask))], p=probs)
                prob=probs[action]
                cnt=0
                while action not in valid_actions:
                    action=np.random.choice([i for i in range(len(action_mask))], p=probs)
                    prob=probs[action] 
                    cnt +=1
                    if cnt>100: 
                        break
                return int(action), float(prob), value
            else:
                raise NotImplementedError('unsupported action selection strategy!')

    def episode_end(self, reward):
        print(self.name+repr(self.agent_id_on_board)+' episode:', self.k_episode, ' ends with result:', reward, 'total taken actions:', self.total_step)
        self.k_episode +=1
        self.total_step=0
        self.seq_state.clear()
        self.retrospect_init_flag=False

