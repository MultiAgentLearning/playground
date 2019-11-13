import numpy as np
from pommerman import utility
from pommerman import constants
from collections import deque
import copy
from pommerman.agents import direction_filter

def position_is_in_corridor(board, position, perpendicular_dirs):
    d1=perpendicular_dirs[0]
    d2=perpendicular_dirs[1]
    p1=utility.get_next_position(position, d1)
    p2=utility.get_next_position(position, d2)

    con1 = ( (not utility.position_on_board(board, p1)) or utility.position_is_wall(board, p1) )
    con2 = ( (not utility.position_on_board(board, p2)) or utility.position_is_wall(board, p2) )
    return con1 and con2

def perpendicular_directions(direction):
    dirs=[constants.Action.Left, constants.Action.Right]
    if direction in dirs:
        dirs=[constants.Action.Up, constants.Action.Down]
    return dirs

def me_to_enemy_all_corridor(board, pos1, pos2):
    assert(pos1[0]==pos2[0] or pos1[1]==pos2[1])
    if pos1[0]==pos2[0]:
        if pos1[1]<pos2[1]:
            direction=constants.Action.Right
        else:
            direction=constants.Action.Left
    else:
        if pos1[0]<pos2[0]:
            direction=constants.Action.Down
        else:
            direction=constants.Action.Up
    p_dirs=perpendicular_directions(direction)
    pos2_next=utility.get_next_position(pos2, direction)
    next_is_impasse=(not utility.position_on_board(board, pos2_next)) or utility.position_is_wall(board, pos2_next)
    if utility.position_on_board(board, pos2_next) and utility.position_is_fog(board, pos2_next):
        next_is_impasse=False
    if not (position_is_in_corridor(board, pos2, p_dirs) and next_is_impasse):
        # pos2:enempy must be in impasse
        return False
    all_corridor_flag=True
    pos=utility.get_next_position(pos1, direction)
    while pos!=pos2:
        if not (utility.position_is_passage(board, pos)):
            all_corridor_flag=False
            break
        if not position_is_in_corridor(board, pos, p_dirs):
            all_corridor_flag=False
            break
        pos=utility.get_next_position(pos, direction)
    return all_corridor_flag    

def must_place_bomb_test(obs):
    board=obs['board']
    enemies=obs['enemies']
    ammo=obs['ammo']
    my_position=obs['position']
    st=obs['blast_strength']
    st=int(st)-1
    if ammo<0:
        return False
    if obs['bomb_life'][my_position]>0:
        #already on bomb
        return False
    if obs['teammate'].value not in obs['alive']:
        e1,e2=enemies[0].value,enemies[1].value
        if e1 in obs['alive'] and e2 in obs['alive']:
            #two enemies alive, only me alive, not do this test..
            return False
    for e in enemies:
        e=e.value
        if e not in obs['alive']:
            continue
        pos=list(zip(*np.where(board==e)))
        if len(pos)==0:
            continue
        pos=pos[0]
        if my_position[0]!=pos[0] and my_position[1]!=pos[1]:
            continue
        if abs(my_position[0]-pos[0])+abs(my_position[1]-pos[1])>st:
            continue
        if me_to_enemy_all_corridor(board, my_position, pos):
            return True
    return False

def position_can_be_bomb_through(board, position):
    if utility.position_is_flames(board, position):
        return True
    if utility.position_is_passage(board, position):
        return True
    if utility.position_is_powerup(board, position):
        return True
    return False

def get_filtered_actions(observ):
    if must_place_bomb_test(observ):
        return [constants.Action.Bomb.value]

    my_position, board, bomb_life, bomb_blast_st, enemies, teammate = \
    observ['position'], observ['board'], observ['bomb_life'], observ['bomb_blast_strength'], observ['enemies'], observ['teammate']
    next_step_flaming_positions=direction_filter.get_next_step_flaming_positions(my_position, board, bomb_life, bomb_blast_st, enemies, teammate)
    ret=direction_filter.get_filtered_directions(observ, next_step_flaming_positions, exclude_kicking=False)

    if bomb_test(observ, next_step_flaming_positions, list(ret)):
        ret.add(constants.Action.Bomb.value)
        
    if len(ret) == 0:
        ret.add(constants.Action.Stop.value)
    return list(ret) 

def bomb_test(observ, flame_positions, remaining_directions):
    if observ['ammo'] < 1:
        return False
    my_position, board, bomb_life, blast_st, enemies, teammate = \
    observ['position'], observ['board'], observ['bomb_life'], observ['bomb_blast_strength'], observ['enemies'], observ['teammate']
    if my_position in flame_positions:
        return False
    my_agent_id=board[my_position]

    teammate_id=observ['teammate'].value
    mate_pos=np.where(board==teammate_id)
    if mate_pos[0].shape[0] >0: 
        m_x,m_y= mate_pos[0][0], mate_pos[1][0] 
        if abs(m_x-my_position[0])+abs(m_y-my_position[1])<=observ['blast_strength']*2: 
            return False

    alive_list=observ['alive']
    if teammate_id not in alive_list:
        #if teammate is dead, be more conservative
        #if it seems there is a bomb, no place bomb
        #OR maybe not place at all in this case?
        return False
        #all_bomb_pos=list(zip(*np.where(bomb_life>0)))
        #if len(all_bomb_pos)>0:
        #    return False
    #not bomb when my_position is covered by a bomb with life<=life_value
    def neighbor_test(my_pos, life_value):
        x,y=my_pos
        i=x-1
        sz=len(board)
        while i>=0:
            position=(i,y)
            if not utility.position_on_board(board, position):
                break
            if int(bomb_life[i,y]) <=life_value and blast_st[i,y] > abs(i-x) :
                return False
            if not position_can_be_bomb_through(board, position):
                break
            i -=1
        i=x+1
        while i<sz:
            position=(i,y)
            if not utility.position_on_board(board, position):
                break
            if int(bomb_life[i,y]) <=life_value and blast_st[i,y] > abs(i-x) :
                return False
            if not position_can_be_bomb_through(board, position):
                break
            i +=1
        j=y-1
        while j>=0:
            position=(x,j)
            if not utility.position_on_board(board, position):
                break
            if int(bomb_life[x,j]) <=life_value and blast_st[x,j] > abs(j-y) :
                return False
            if not position_can_be_bomb_through(board, position):
                break
            j -=1
        j=y+1
        while j<sz:
            position=(x,j)
            if not utility.position_on_board(board, position):
                break
            if int(bomb_life[x,j]) <=life_value and blast_st[x,j] > abs(j-y) :
                return False
            if not position_can_be_bomb_through(board, position):
                break
            j +=1
        return True
    if not neighbor_test(my_position, life_value=10):
        return False

    directions=[constants.Action.Down, constants.Action.Up,constants.Action.Left, constants.Action.Right]
    #not place bomb when agent is at the intersections of two or more corridors
    corridors=[]
    for d in directions:
        d=constants.Action(d)
        next_pos=utility.get_next_position(my_position, d)
        if not utility.position_on_board(board, next_pos):
            continue
        if not position_can_be_bomb_through(board, next_pos):
            continue
        if not neighbor_test(next_pos, life_value=10):
            return False
        perpendicular_dirs=[constants.Action.Left, constants.Action.Right] 
        if d == constants.Action.Left or d == constants.Action.Right:
            perpendicular_dirs=[constants.Action.Down, constants.Action.Up]
        ret=direction_filter.is_in_corridor(board, next_pos, perpendicular_dirs)
        corridors.append(ret)
    if len(corridors)>=2 and all(corridors):
        return False
    return True
