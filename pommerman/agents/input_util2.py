import numpy as np
from pommerman import utility
from pommerman import constants
from collections import deque

def get_intermediate_rewards(prev_observations, cur_observations, position_queue):
    # Note: only for team env
    r=[0.0, 0.0, 0.0, 0.0]
    for i in range(4):
        prev_alive=prev_observations[i]['alive']
        prev_n_enemy=0 
        for e in prev_observations[i]['enemies']:
            if e.value in prev_alive:
                prev_n_enemy +=1

        prev_n_teammate=1 if prev_observations[i]['teammate'].value in prev_alive else 0
        prev_can_kick=prev_observations[i]['can_kick']
        prev_n_ammo=prev_observations[i]['ammo']
        prev_n_blast=prev_observations[i]['blast_strength']
        prev_position=prev_observations[i]['position']
        prev_wood_positions=list(zip(*np.where( prev_observations[i]['board']==constants.Item.Wood.value )))

        cur_alive=cur_observations[i]['alive']
        cur_n_enemy=0
        for e in cur_observations[i]['enemies']:
            if e.value in cur_alive:
                cur_n_enemy +=1

        cur_n_teammate=1 if cur_observations[i]['teammate'].value in cur_alive else 0
        cur_can_kick=cur_observations[i]['can_kick']
        cur_n_ammo=cur_observations[i]['ammo']
        cur_n_blast=cur_observations[i]['blast_strength']
        cur_position=cur_observations[i]['position']

        if prev_n_enemy - cur_n_enemy > 0:
            r[i] += (prev_n_enemy-cur_n_enemy)*0.5
        if prev_n_teammate - cur_n_teammate > 0:
            r[i] -= (prev_n_teammate-cur_n_teammate)*0.5
        if not prev_can_kick and cur_can_kick:
            r[i] += 0.02
        if cur_n_ammo - prev_n_ammo>0:
            r[i] += 0.00
        if cur_n_blast - prev_n_blast >0:
            r[i] += 0.00
        if cur_position not in position_queue:
            r[i] +=0.000
            position_queue.append(cur_position)
        for row,col in prev_wood_positions:
            cur_board=cur_observations[i]['board']
            if not utility.position_is_wall(cur_board, (row, col)) and not utility.position_is_fog(cur_board, (row,col)):
                r[i] +=0.000

    #0 2 teammates, 1 3 teammates
    team_spirit=0.2
    r0=r[0]*(1-team_spirit)+team_spirit*r[2]
    r1=r[1]*(1-team_spirit)+team_spirit*r[3]
    r2=r[2]*(1-team_spirit)+team_spirit*r[0]
    r3=r[3]*(1-team_spirit)+team_spirit*r[1]

    mean1=(r0+r2)/2.0
    mean2=(r1+r3)/2.0
    #make sure it is zero-sum
    r=[r0-mean2, r1-mean1, r2-mean2, r3-mean1]
    #print(r)
    return r

def make_featurize_planes(obs, timestep, retrospect_board, retrospect_bomb_life, retrospect_bomb_blast_strength):
    """ 13 feature planes, adapted from envs.v0.featurize """
    board = obs["board"].astype(np.float32)
    bomb_blast_strength = obs["bomb_blast_strength"].astype(np.float32)
    bomb_life = obs["bomb_life"].astype(np.float32)
    planes=[board, bomb_blast_strength, bomb_life]

    #position = utility.make_np_float(obs["position"])
    posi_plane=np.zeros_like(board)
    posi_plane[obs["position"]]=1.0

    mate=obs['teammate'].value
    mate_pos=np.where(mate==board)
    mate_plane=np.zeros_like(board)
    if mate_pos[0].shape[0] >0:
        posi_plane[mate_pos[0][0], mate_pos[1][0]]=1.0
    for e in obs['enemies']:
        e_pos=np.where(e.value == board)
        if e_pos[0].shape[0] >0:
            posi_plane[e_pos[0][0], e_pos[1][0]]=1.0

    planes.append(posi_plane)

    ammo_plane=np.zeros_like(board)
    #ammo = utility.make_np_float([obs["ammo"]])
    ammo_plane.fill(obs['ammo'])
    planes.append(ammo_plane)

    blast_st_plane=np.zeros_like(board)
    blast_strength = utility.make_np_float([obs["blast_strength"]])
    blast_st_plane.fill(blast_strength[0])
    planes.append(blast_st_plane)

    can_kick = utility.make_np_float([obs["can_kick"]])
    can_kick_plane=np.zeros_like(board)
    can_kick_plane.fill(can_kick[0])
    planes.append(can_kick_plane)

    #teammate = utility.make_np_float([obs["teammate"].value])
    mate=obs['teammate'].value
    mate_plane=np.zeros_like(board)
    if mate in obs['alive']:
        mate_plane.fill(mate)
    planes.append(mate_plane)
    
    #enemies = utility.make_np_float([e.value for e in obs["enemies"]])
    enemy_plane=np.zeros_like(board)
    for e in obs['enemies']:
        if e.value in obs['alive']:
            enemy_plane +=e.value
    planes.append(enemy_plane)

    time_step_plane=np.zeros_like(board)
    time_step_plane.fill(timestep)
    planes.append(time_step_plane)

    agent_id_on_board=board[obs['position']]
    id_plane=np.zeros_like(board)
    id_plane.fill(agent_id_on_board)
    planes.append(id_plane)

    planes.append(retrospect_board)
    planes.append(retrospect_bomb_life)
    planes.append(retrospect_bomb_blast_strength)
    ret = np.stack(planes)
    #print('feature shape:', ret.shape)
    _update_retrospect_info(obs, retrospect_board, retrospect_bomb_life, retrospect_bomb_blast_strength)
    return ret


def _update_retrospect_info(obs, retrospect_board, retrospect_bomb_life, retrospect_bomb_blast_strentth):
    sz=len(retrospect_board)
    for i in range(sz):
        for j in range(sz):
            if retrospect_bomb_life[i][j] == 0:
                retrospect_bomb_blast_strentth[i][j]=0
            else:
                retrospect_bomb_life[i,j] -=1
            
    for i in range(sz):
        for j in range(sz):
            if obs['board'][i,j]!=constants.Item.Fog.value:
                retrospect_board[i,j]=obs['board'][i,j]
                retrospect_bomb_life[i,j]=obs['bomb_life'][i,j]
                retrospect_bomb_blast_strentth[i,j]=obs['bomb_blast_strength'][i,j]

