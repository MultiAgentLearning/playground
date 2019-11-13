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
    batch_sum_exp_logits=(torch.sum(batch_exp_logits, dim=1, keepdim=True)+1e-8)
    batch_probs=batch_exp_logits/batch_sum_exp_logits
    batch_probs = batch_probs + 1e-5
    return batch_probs

def masked_log_probs(batch_probs, batch_mask):
    batch_log_probs=batch_mask.float()*torch.log(batch_probs)
    return batch_log_probs

class CNN_LSTM(nn.Module):
    """
    1-layer LSTM
    Support variable sequence lengths within mini-batch

    For each LSTM cell:
    batch input x_t -> CNN -> batch vectors \hat{x}_t-> LSTM  -> batch action vectors a_t
    Args:
    input_shape: tuple, e.g., (9, 11,11): there are 9 11x11 planes
    n_output_actions: int, number of output actions from each LSTM cell
    """
    def __init__(self, input_feature_shape, n_actions,
                 n_filters_per_layer=64, n_cnn_layers=8, n_fc_units_cnn=64, lstm_out_size=64, device_string='cpu'):
        ''' init stuff for each LSTM cell  '''
        super().__init__()
        input_depth, w1 ,w2 = input_feature_shape
        assert(w1==w2) # pommerman should have square board
        self.n_layers=n_cnn_layers
        self.n_filters =n_filters_per_layer
        self.lstmcell_input_size = n_fc_units_cnn # int
        self.lstmcell_output_size = lstm_out_size  # int
        self.n_actions=n_actions
        self.input_shape=input_feature_shape
        self.device_string=device_string

        #self.bn=[None]*self.n_layers
        self.conv=[None]*self.n_layers
        device = torch.device(self.device_string if torch.cuda.is_available() else 'cpu')
        if self.device_string[-1].isdigit():
            k=int(self.device_string[-1])
            torch.cuda.set_device(k)
        
        print('device:', device)
        for i in range(self.n_layers):
            #self.bn[i]=nn.BatchNorm2d(n_filters_per_layer).to(device)
            if i == 0: 
                self.conv[i]=nn.Conv2d(input_depth, self.n_filters, kernel_size=3, stride=1, padding=1).to(device)
            else: 
                self.conv[i]=nn.Conv2d(self.n_filters, self.n_filters, kernel_size=3, stride=1, padding=1).to(device)

        self.fc_cnn=nn.Linear(self.n_filters*w1*w2, self.lstmcell_input_size).to(device)
        self.lstm =nn.LSTM(n_fc_units_cnn, self.lstmcell_output_size, batch_first=True).to(device)
        self.fc_p_head=nn.Linear(self.lstmcell_output_size, 128).to(device)
        self.fc_p_head2=nn.Linear(128, self.n_actions).to(device)
        
        self.fc_v_head=nn.Linear(self.lstmcell_output_size, 128).to(device)
        self.fc_v_head2=nn.Linear(128, 1).to(device)

    def _cnn(self, h):
        # using CNN to transfrom input feature planes into a vector
        h=h.unsqueeze(0) # pretend to be a batch of only one input
        for i in range(self.n_layers):
            h=self.conv[i](h)
            #h=self.bn[i](h)
            h=F.relu(h)
        h=h.view(-1, h.shape[1]*h.shape[2]*h.shape[3])
        h=self.fc_cnn(h)
        h=F.relu(h)
        return h.squeeze(0)

    def _two_head(self, lstm_out):
        #lstm_out should be with shape [n, m]
        p,v=self.fc_p_head(lstm_out), self.fc_v_head(lstm_out)
        p,v=F.relu(p), F.relu(v)
        p,v=self.fc_p_head2(p), self.fc_v_head2(v)
        return p,v

    #A_s is Generalized Advantage Estimate
    #forward batch seq states then compute the loss
    def forward(self, batch_seq_trans, only_inference=False, objective='ppo', p_coeff=1.0, entropy_coeff=0.01, v_coeff=1.0):
        batch_seq_trans.sort(key=lambda seq: len(seq), reverse=True)
        seq_lens=[len(seq) for seq in batch_seq_trans]
        batch_size=len(batch_seq_trans)
        max_len=max(seq_lens)
        device = torch.device(self.device_string if torch.cuda.is_available() else 'cpu')

        batch_padded_s=torch.zeros(batch_size, max_len, self.lstmcell_input_size).to(device).float()
        if not only_inference:
            batch_padded_a=torch.zeros(batch_size, max_len).to(device).int()
            batch_padded_A_s=torch.zeros(batch_size, max_len).to(device).float()
            batch_padded_v_s=torch.zeros(batch_size, max_len).to(device).float()
            batch_padded_p_a=torch.zeros(batch_size, max_len).to(device).float()
            batch_padded_R=torch.zeros(batch_size, max_len).to(device).float()
            batch_padded_action_mask=torch.zeros(batch_size, max_len, self.n_actions).to(device).int()
        for i in range(batch_size):
            for j in range(seq_lens[i]): 
                if only_inference:
                    #input is just batch seq of states
                    s=batch_seq_trans[i][j]
                    s=torch.from_numpy(s).to(device).float()
                    batch_padded_s[i][j] = torch.tensor(self._cnn(s), device=device).float()
                    continue
                item=batch_seq_trans[i][j]
                s,a,A_s,v_s,p_a, R, a_m=item.state,item.action,item.reward,item.value_of_state,item.prob_of_action, item.cumulative_return, item.action_mask
                s=torch.from_numpy(s).to(device).float()
                batch_padded_s[i][j] = torch.tensor(self._cnn(s), device=device).float()
                batch_padded_a[i][j]=torch.tensor(a).to(device).long()
                batch_padded_A_s[i][j]=torch.tensor(A_s).to(device).float()
                batch_padded_v_s[i][j]=torch.tensor(v_s).to(device).float()
                batch_padded_p_a[i][j]=torch.tensor(p_a).to(device).float()
                batch_padded_R[i][j]=torch.tensor(R).to(device).float()
                batch_padded_action_mask[i][j]=torch.from_numpy(a_m).to(device).int()
    
        batch_packed_s=torch.nn.utils.rnn.pack_padded_sequence(batch_padded_s, seq_lens, batch_first=True)

        if not only_inference:
            batch_packed_a=torch.nn.utils.rnn.pack_padded_sequence(batch_padded_a, seq_lens, batch_first=True)
            batch_packed_A_s=torch.nn.utils.rnn.pack_padded_sequence(batch_padded_A_s, seq_lens, batch_first=True)
            batch_packed_v_s=torch.nn.utils.rnn.pack_padded_sequence(batch_padded_v_s, seq_lens, batch_first=True)
            batch_packed_p_a=torch.nn.utils.rnn.pack_padded_sequence(batch_padded_p_a, seq_lens, batch_first=True)
            batch_packed_R=torch.nn.utils.rnn.pack_padded_sequence(batch_padded_R, seq_lens, batch_first=True)
            batch_packed_action_mask=torch.nn.utils.rnn.pack_padded_sequence(batch_padded_action_mask, seq_lens, batch_first=True)

        self.lstm.flatten_parameters()
        out, (ct, ht)=self.lstm(batch_packed_s)
        self.lstm.flatten_parameters()
        #print('requires_grad? ', out.data.requires_grad)
        p_logits,v_logit=self._two_head(out.data)

        if only_inference:
            return p_logits, v_logit
        #print('a shape:', batch_packed_a.data.shape)

        zero_tensor=torch.tensor(0.0).to(device).float()
        probs=masked_softmax(p_logits, batch_packed_action_mask.data) #probs=F.softmax(p_logits, dim=1)
        log_probs=masked_log_probs(probs, batch_packed_action_mask.data) #log_probs=F.log_softmax(p_logits, dim=1)
#print('probs shape', probs.shape)
        entropy=-(probs*log_probs).sum(1).detach()
#print('entropy shape', entropy.shape)
        advantage = batch_packed_A_s.data
        advantage = (advantage - advantage.mean())/(1e-8 + advantage.std())
#print('advantage shape', advantage.shape) 

        CLIP_RANGE=0.2
        R=batch_packed_R.data
        #print('R:',R)
        v_old=batch_packed_v_s.data
        v_predict=torch.tanh(v_logit)
        v_pred_clipped= v_old + torch.clamp(v_predict-v_old, -CLIP_RANGE, CLIP_RANGE)
        v_loss1=(v_predict-R)**2
        v_loss2=(v_pred_clipped - R)**2
        value_loss = 0.5*torch.max(v_loss1, v_loss2)

        target_action_probs=torch.gather(probs,1, batch_packed_a.data.unsqueeze(1).long()).squeeze()
        target_action_log_probs=torch.gather(log_probs,1, batch_packed_a.data.unsqueeze(1).long()).squeeze()
        if objective == 'maximum_likelihood':
            return p_logits, v_logit, -target_action_log_probs.mean()
        if objective == 'a2c':
            #implemet a2c loss
            policy_loss=-target_action_log_probs*advantage.detach()
        else:
            assert(objective == 'ppo')
            ratio = torch.div(target_action_probs, batch_packed_p_a.data)
            #print('ratio, shape', ratio.shape) 
            policy_loss=-torch.min(advantage.detach()*ratio, advantage.detach()*torch.clamp(ratio, 1-CLIP_RANGE, 1+CLIP_RANGE))
        loss = p_coeff*policy_loss.mean() - entropy_coeff*entropy.mean() + v_coeff*value_loss.mean()
        return p_logits.detach(), v_logit.detach(), loss

if __name__ == "__main__": 
    ''' make a dummy input forward see if every goes as expected '''
    # nn should be able to fit random data perfectly. 
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    nn_model=CNN_LSTM(input_feature_shape=(9, 11,11), n_actions=6, device_string='cuda')
    s=torch.zeros(9,11,11).to(device)
    h=nn_model._cnn(s)
    print(h.shape,'expected:[' +repr(nn_model.lstmcell_input_size)+']')  # expected [lstm_input_size] 

    batch_seq_s=[]
    for i in range(2): 
        k=2 if i==0 else 3 #random a seq length
        #[s1,s2,s3,s4]
        seq_s=[np.zeros(shape=(9,11,11), dtype=np.float32) for j in range(k)]
        batch_seq_s.append(seq_s)

    d=nn_model(batch_seq_s, only_inference=True)
    print(d, 'Expected:p_logits and v_logit of shape [?, 6], [?] where ? is the total states')
    #now try a single sequence input
    batch_seq_s2=[[np.zeros(shape=(9,11,11), dtype=np.float32) for i in range(4)]]
    d=nn_model.forward(batch_seq_s2, only_inference=True)
    print(d)

    #now try a training on fixed random data
    print('train on some random data')
    nn_model.train()
    batch_seq_trans=[]
    for i in range(2):
        k=2 if i==0 else 3 #random a seq length
        #(s,a,A_s,v_s,p_a)
        seq_trans=[Transition(np.zeros(shape=(9,11,11), dtype=np.float32), 1, 0.9, 0.8, 0.6,0.0) for j in range(k)]
        batch_seq_trans.append(seq_trans)
    p_logits, v_logit, loss=nn_model(batch_seq_trans, only_inference=False)
    print(loss)
    opt=optim.Adam(nn_model.parameters(), lr=1e-3)
    #opt=optim.SGD(nn_model.parameters(), lr=0.01, momentum=0.9, weight_decay=0.9)
    
    for i in range(100):
        opt.zero_grad()
        #usually, prepare data X=[], batch_seq_target
        objective='maximum_likelihood'
        objective='a2c'
        #objective='ppo'
        p_logits, v_logit, loss=nn_model(batch_seq_trans, only_inference=False, objective=objective, entropy_coeff=0.0)
        loss.backward()
        opt.step()
        print('--step', i, 'loss:', loss.data.item())
    #now try save and load model parameters
    torch.save(nn_model.state_dict(), '/tmp/ppo_torch_test.pt')
