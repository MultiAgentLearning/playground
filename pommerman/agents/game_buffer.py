from collections import namedtuple
import random

#Transition=namedtuple('Transition', ['state', 'action', 'reward', 'value_of_state', 'prob_of_action'])
Transition=namedtuple('Transition', ['state', 'action', 'reward', 'value_of_state', 'prob_of_action','cumulative_return', 'action_mask'])


class GameBuffer(object):
    '''
    DataFormat: each element in memory is a sequence of (state,action,reward,value_of_state,prob_of_action)
    sample: sample a batch of sequences
    '''
    def __init__(self, capacity):
        self.capacity = capacity
        self.memory = []
        self.position = 0

    def push(self, game):
        if len(self.memory) < self.capacity:
            self.memory.append(None)
        self.memory[self.position] = game
        self.position = (self.position + 1) % self.capacity

    def sample(self, batch_size):
        # reward is actually GAE
        batch_seq_trans=random.sample(self.memory, batch_size)
        batch_s=[]
        batch_a=[]
        batch_A_s=[]
        batch_value_of_state=[]
        batch_prob_of_action=[]
        batch_R=[]
        batch_action_mask=[]
        for seq in batch_seq_trans:
            for trans in seq:
                #if len([ii for ii in trans.action_mask if ii>0])<=1:
                #    continue
                batch_s.append(trans.state)
                batch_a.append(trans.action)
                batch_A_s.append(trans.reward)
                batch_value_of_state.append(trans.value_of_state)
                batch_prob_of_action.append(trans.prob_of_action)
                batch_R.append(trans.cumulative_return)
                batch_action_mask.append(trans.action_mask)
        return batch_s,batch_a,batch_A_s, batch_value_of_state, batch_prob_of_action, batch_R, batch_action_mask

    def __len__(self):
        return len(self.memory)

def compute_advantage(seq_trans, gae_n_step, gae_discount, gae_lambda):
    # Given a sequence of (s,a,r,p_a,v_s) compute the advantage function for each
    # I.e. Replace r with advantage A_s
    # A_s = \sum_{i=0}^{T} (\lambda \gamma)^\delta_i
    # \delta_t = r + \gamma V(S_{t+1}) - V(S_t)

    delta = []
    Returns=[]
    for k,trans in enumerate(seq_trans):
        r=trans.reward
        value_of_state=trans.value_of_state
        if k != len(seq_trans) - 1:
            value_of_next_state = seq_trans[k+1].value_of_state
        else:
            value_of_next_state = 0.0
        delta.append(r+gae_discount*value_of_next_state - value_of_state)
        discount=1.0
        Returns.append(0.0)
        for j in range(k, len(seq_trans), 1):
           Returns[k]  = discount*seq_trans[j].reward
           #Returns[k]  += discount*seq_trans[j].reward
           #discount=discount*gae_discount
    
    for k, trans in enumerate(seq_trans):
        adv=0.0
        factor=1.0
        for i in range(gae_n_step):
            if k+i >= len(seq_trans):
                break
            adv += factor*delta[k+i]
            factor = factor*gae_discount*gae_lambda
        ret=Returns[k]
        v=trans.value_of_state
        mask=trans.action_mask
        #seq_trans[k] = Transition(state=trans.state, action=trans.action, reward=adv, value_of_state=v, prob_of_action=trans.prob_of_action)
        seq_trans[k] = Transition(state=trans.state, action=trans.action, reward=adv, value_of_state=v, prob_of_action=trans.prob_of_action, cumulative_return=ret, action_mask=mask)
    return seq_trans

def split_to_chunks(seq_trans, chunk_len):
    """Yield successive chunk_len-sized chunks."""
    for i in range(0, len(seq_trans), chunk_len):
        yield seq_trans[i:i + chunk_len]

if __name__ == "__main__":
    import numpy as np
    mask=np.zeros(shape=(6,), dtype=np.int16)
    x1=Transition(state=np.zeros(shape=(3,3), dtype=np.float32), action=1, reward=0.8, value_of_state=0.5, prob_of_action=0.9, cumulative_return=0.0, action_mask=mask)
    x2=Transition(state=np.zeros(shape=(3,3), dtype=np.float32), action=1, reward=0.8, value_of_state=0.5, prob_of_action=0.9, cumulative_return=.0, action_mask=mask)
    x3=Transition(state=np.zeros(shape=(3,3), dtype=np.float32), action=1, reward=0.8, value_of_state=0.5, prob_of_action=0.9, cumulative_return=0.0, action_mask=mask)
    x4=Transition(state=np.zeros(shape=(3,3), dtype=np.float32), action=1, reward=0.8, value_of_state=0.5, prob_of_action=0.9, cumulative_return=-0.0, action_mask=mask)
    seq_trans=[x1,x2,x3,x4]
    print(seq_trans)
    gae_discount=0.99
    gae_lambda=0.1
    gae_n_step=2
    print('gae_discount, gae_lambda, gae_n_step', gae_discount, gae_lambda, gae_n_step)
    print(compute_advantage(seq_trans, gae_n_step, gae_discount, gae_lambda))
    print('some test')
