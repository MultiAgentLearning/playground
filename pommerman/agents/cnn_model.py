import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

import numpy as np
import math
import random

from itertools import count

import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from pommerman.agents.game_buffer import Transition

def masked_softmax(batch_logits, batch_mask):
    batch_max=torch.max(batch_logits, dim=1, keepdim=True)[0]
    batch_exp_logits=torch.exp(batch_logits - batch_max)*batch_mask.float()
    batch_exp_logits = batch_exp_logits + 1e-8
    batch_sum_exp_logits=(torch.sum(batch_exp_logits, dim=1, keepdim=True))
    batch_probs=batch_exp_logits/batch_sum_exp_logits
    return batch_probs

def masked_log_probs(batch_probs, batch_mask):
    batch_probs = batch_probs + 1e-8
    batch_log_probs=batch_mask.float()*torch.log(batch_probs)
    return batch_log_probs

class CNNBatchNorm(nn.Module):
    """
    feedforward CNN with batch normalization
    """
    def __init__(self, input_feature_shape, n_actions,
                 n_filters_per_layer=64, n_cnn_layers=8, n_fc_units_cnn=64):
        ''' init stuff for each LSTM cell  '''
        super().__init__()
        input_depth, w1 ,w2 = input_feature_shape
        assert(w1==w2) # pommerman should have square board
        self.n_layers=n_cnn_layers
        self.n_filters =n_filters_per_layer
        self.n_actions=n_actions
        self.input_shape=input_feature_shape

        self.bn=torch.nn.ModuleList([torch.nn.BatchNorm2d(self.n_filters)])
        self.bn.extend([torch.nn.BatchNorm2d(self.n_filters) for i in range(self.n_layers-1)])

        self.conv=torch.nn.ModuleList([nn.Conv2d(input_depth, self.n_filters, kernel_size=3, stride=1, padding=1)])
        self.conv.extend([nn.Conv2d(self.n_filters, self.n_filters, kernel_size=3, stride=1, padding=1) for i in range(self.n_layers-1)])

        self.p_cnn=torch.nn.Conv2d(self.n_filters, 2, kernel_size=1, stride=1, padding=0)
        self.p_bn=torch.nn.BatchNorm2d(2)
        self.fc_p_head=nn.Linear(2*w1*w2, self.n_actions)

        self.v_cnn=torch.nn.Conv2d(self.n_filters,1, kernel_size=1, stride=1, padding=0)
        self.v_bn=torch.nn.BatchNorm2d(1)
        self.fc_v_head=nn.Linear(1*w1*w2, 32)
        self.fc_v_head2=nn.Linear(32, 1)

    def _cnn(self, h):
        for i in range(self.n_layers):
            h=self.conv[i](h)
            h=F.relu(h)
            #h=self.bn[i](h)
        return h

    def _two_head(self, cnn_out):
        p=self.p_cnn(cnn_out)
        p=F.relu(p)
        #p=self.p_bn(p)
        p=p.view(-1, p.shape[1]*p.shape[2]*p.shape[3])
        p=self.fc_p_head(p)

        v=self.v_cnn(cnn_out)
        v=F.relu(v)
        #v=self.v_bn(v)
        v=v.view(-1,v.shape[1]*v.shape[2]*v.shape[3])
        v=self.fc_v_head(v)
        v=F.relu(v)
        v=self.fc_v_head2(v)

        return p,v

    def compute_loss(self, batch_p_logits, batch_v_logit, batch_a, batch_A_s, batch_value_of_state, batch_prob_of_action, batch_R, batch_action_mask,\
            objective='ppo', p_coeff=1.0, entropy_coeff=0.01, v_coeff=1.0):
        probs=masked_softmax(batch_p_logits, batch_action_mask) #probs=F.softmax(p_logits, dim=1)
        log_probs=masked_log_probs(probs, batch_action_mask) 
        #log_probs=F.log_softmax(batch_p_logits, dim=1)

        entropy=-(probs*log_probs).sum(1).detach()
        #print('entropy shape', entropy.shape)
        advantage = batch_A_s
        advantage = (advantage - advantage.mean())/(1e-8 + advantage.std())

        CLIP_RANGE=0.2
        R=batch_R
        v_old=batch_value_of_state
        v_predict=torch.tanh(batch_v_logit)
        v_pred_clipped= v_old + torch.clamp(v_predict-v_old, -CLIP_RANGE, CLIP_RANGE)
        v_loss1=(v_predict-R)**2
        v_loss2=(v_pred_clipped - R)**2
        value_loss = 0.5*torch.max(v_loss1, v_loss2)
        #value_loss = 0.5*v_loss1

        target_action_probs=torch.gather(probs,1, batch_a.unsqueeze(1).long()).squeeze()
        target_action_log_probs=torch.gather(log_probs,1, batch_a.unsqueeze(1).long()).squeeze()
        if objective == 'maximum_likelihood':
            return batch_p_logits, batch_v_logit, -target_action_log_probs.mean()
        if objective == 'a2c':
            #implemet a2c loss
            policy_loss=-target_action_log_probs*advantage.detach()
        else:
            assert(objective == 'ppo')
            ratio = torch.div(target_action_probs, batch_prob_of_action)
            #print('ratio, shape', ratio.shape) 
            policy_loss=-torch.min(advantage.detach()*ratio, advantage.detach()*torch.clamp(ratio, 1-CLIP_RANGE, 1+CLIP_RANGE))
        loss = p_coeff*policy_loss.mean() - entropy_coeff*entropy.mean() + v_coeff*value_loss.mean()
        return loss

        
    #A_s is Generalized Advantage Estimate
    #forward batch states then compute the loss
    def forward(self, batch_s):
        #Transition=namedtuple('Transition', ['state', 'action', 'reward', 'value_of_state', 'prob_of_action','cumulative_return', 'action_mask'])
        h=self._cnn(batch_s)
        batch_p_logits, batch_v_logit=self._two_head(h)
        return batch_p_logits, batch_v_logit

        
if __name__ == "__main__": 
    ''' make a dummy input forward see if every goes as expected '''
    # nn should be able to fit random data perfectly. 
    nn_model=CNNBatchNorm(input_feature_shape=(10, 11,11), n_actions=6)
    batch_trans=[]
    import random
    for i in range(10):
        s=torch.rand(10,11,11)
        s=torch.zeros(10,11,11)
        s[0][0][0]+=float(i)
        #a=random.randint(0,5)
        a=i%6
        r=1.0
        v=0.5
        p=0.4
        R=0.9
        action_mask=np.random.choice([0, 1], size=(6,), p=[0./3, 3./3])
        trans=Transition(state=s, action=a, reward=r, value_of_state=v, prob_of_action=p, cumulative_return=R, action_mask=action_mask)
        batch_trans.append(trans)

    opt=optim.Adam(nn_model.parameters(), lr=1e-3)
    #opt=optim.SGD(nn_model.parameters(), lr=0.01, momentum=0.9)
    
    for i in range(1000):
        opt.zero_grad()
        #usually, prepare data X=[], batch_seq_target
        objective='maximum_likelihood'
        #objective='a2c'
        #objective='ppo'
        p_logits, v_logit, loss=nn_model(batch_trans, only_inference=False, objective=objective, entropy_coeff=0.0)
        loss.backward()
        opt.step()
        print('--step', i, 'loss:', loss.data.item())
    #now try save and load model parameters
    torch.save(nn_model.state_dict(), '/tmp/ppo_torch_test.pt')

