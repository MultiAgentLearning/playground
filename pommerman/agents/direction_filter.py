import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))
import numpy as np
from pommerman import utility
from pommerman import constants
from collections import deque
import copy
import math

def step_to(obs, new_position, lay_bomb=False):
    """return: a copy of new observation after stepping into new_position. 
       If lay_bomb==True, it is actually two-step change (i.e., lay bomb then go to new_position)
    """
    assert(utility.position_is_passable(obs['board'], new_position, obs['enemies']))
    new_obs=copy.deepcopy(obs)
    sz=len(obs['board'])
    old_board=obs['board']
    old_position=obs['position']
    old_position_value = constants.Item.Bomb.value
    if not lay_bomb:
        #if not lay bomb, the agent could on a bomb, making a 1-step move to new_position
        old_position_value = constants.Item.Bomb.value if obs['bomb_life'][old_position] > 0 else \
        constants.Item.Passage.value
    #1.move agent to new position, 2. update board, bomb_blast_st, bomb_life, position
    new_obs['position']=new_position #update position
    new_obs['board'][old_position]=old_position_value # update board
    agent_id=old_board[old_position]
    new_obs['board'][new_position]=agent_id # update board
    if lay_bomb:
        new_obs['bomb_blast_strength'][old_position]=obs['blast_strength'] #update blast_st
        new_obs['bomb_life'][old_position]=constants.DEFAULT_BOMB_LIFE     #update bomb_life
    for i in range(sz):
        for j in range(sz):
            time_step=2 if lay_bomb else 1
            if new_obs['bomb_life'][i,j] < 2:
                continue
            new_obs['bomb_life'][i,j] = max(1, new_obs['bomb_life'][i,j]-time_step)
    return new_obs

def kick_test(board, blast_st, bomb_life, my_position, direction):
    def moving_bomb_check(moving_bomb_pos, p_dir, time_elapsed):
        pos2=utility.get_next_position(moving_bomb_pos, p_dir)
        dist=0
        for i in range(10):
            dist +=1
            if not utility.position_on_board(board, pos2):
                break
            if not position_is_passable(board, pos2):
                break
            life_now=bomb_life[pos2] - time_elapsed
            if bomb_life[pos2]>0 and life_now>=-2 and life_now <= 0 and dist<blast_st[pos2]:
                return False
            pos2=utility.get_next_position(pos2, p_dir)
        return True
    next_position=utility.get_next_position(my_position, direction)
    assert(utility.position_in_items(board, next_position, [constants.Item.Bomb]))
    life_value=int(bomb_life[next_position])
    strength=int(blast_st[next_position])
    dist=0
    pos=utility.get_next_position(next_position, direction)
    perpendicular_dirs=[constants.Action.Left, constants.Action.Right] 
    if direction == constants.Action.Left or direction == constants.Action.Right:
        perpendicular_dirs=[constants.Action.Down, constants.Action.Up]
    for i in range(life_value): 
        if utility.position_on_board(board, pos) and utility.position_is_passage(board, pos):
            #do a check if this position happens to be in flame when the moving bomb arrives!
            if not (moving_bomb_check(pos, perpendicular_dirs[0], i) and moving_bomb_check(pos, perpendicular_dirs[1], i)):
                break
            dist +=1 
        else:
            break
        pos=utility.get_next_position(pos, direction)
        #can kick and kick direction is valid
    return dist > strength
              
def get_filtered_directions(obs, next_step_flaming_positions, exclude_kicking=False):
    ret=set()
    my_position, board, blast_st, bomb_life, can_kick=obs['position'], obs['board'], obs['bomb_blast_strength'], obs['bomb_life'], obs['can_kick']
    enemies=obs['enemies']
    teammate=obs['teammate'].value
    
    kick_dir=None
    could_be_occupied_dir=None
    for direction in [constants.Action.Left, constants.Action.Up, constants.Action.Right, constants.Action.Down]:
        position = utility.get_next_position(my_position, direction) 
        if not utility.position_on_board(board, position):
            continue
        if position in next_step_flaming_positions: 
            continue

        if not exclude_kicking and utility.position_in_items(board, position, [constants.Item.Bomb]) and can_kick:
            #filter kick if kick is unsafe
            if kick_test(board, blast_st, bomb_life, my_position, direction): 
                ret.add(direction.value)
                kick_dir=direction.value

        if position_is_passable(board, position, enemies):
            if bomb_life[my_position]>0 and not agent_on_bomb_next_move_test(my_position, direction, board, bomb_life, blast_st):
                #if moving to this passage leads to a long corridor
                continue
            
            if my_position in next_step_flaming_positions and not _opponent_test(board, position, enemies):
                # if I am in danger, I should not go to a position which may also be the next position of enemies
                # unless this is the only passage
                could_be_occupied_dir=direction.value
                continue
            if not _teammate_test(board, position, teammate, next_step_flaming_positions):
                continue
            new_obs=step_to(obs, position)
            #one step lookahead search see if this new position would lead to no way dodge 
            #if not is_going_into_siege(observ, old_pos, new_pos):
            flame_positions=next_step_flaming_positions 
            # after step to the new_position, when check around, remember to 
            # exclude those flame positions computed previously since they must have been filed with flames 
            if not position_has_no_escape(new_obs, flame_positions, consider_enemy=False):
                ret.add(direction.value)
    if len(ret)==0 and could_be_occupied_dir is not None:
        ret.add(could_be_occupied_dir)
    if my_position not in next_step_flaming_positions and (not (kick_dir and len(ret)==1)):
        new_obs=step_to(obs, my_position)
        if not (bomb_life[my_position]>0 and bomb_life[my_position]<=3) and not position_has_no_escape(new_obs, next_step_flaming_positions, consider_enemy=True): 
            ret.add(constants.Action.Stop.value)
    return ret

def _opponent_test(board, candidate_position, enemies):
    assert(position_is_passable(board, candidate_position))
    #make sure this passage is not next to the opponent, otherwise the opponent may come to this position
    for direction in [constants.Action.Left, constants.Action.Up, constants.Action.Right, constants.Action.Down]:
        position = utility.get_next_position(candidate_position, direction) 
        if not utility.position_on_board(board, position):
            continue
        if utility.position_is_enemy(board, position, enemies):
            return False
    return True

def _teammate_test(board, candidate_position, teammate, next_step_flaming_positions):
    assert(position_is_passable(board, candidate_position))
    #make sure this passage is not next to your teammate if your teammate is in "danger" (thus teammate must come here to be safe)
    for direction in [constants.Action.Left, constants.Action.Up, constants.Action.Right, constants.Action.Down]:
        position = utility.get_next_position(candidate_position, direction) 
        if not utility.position_on_board(board, position):
            continue
        if board[position] == teammate and position in next_step_flaming_positions:
            return False
    return True

def _all_bomb_real_life(board, bomb_life, bomb_blast_st):
    def bomb_real_life(bomb_position, board, bomb_blast_st, bomb_life):
        """One bomb's real life is the minimum life of its adjacent bomb. 
           Not that this could be chained, so please call it on each bomb mulitple times until
           converge
        """
        x,y=bomb_position
        i=x
        min_life=900
        sz=len(board)
        while i>=0: 
            pos=(i,y)
            dist=abs(i-x)
            if utility.position_is_wall(board, pos):
                break
            if bomb_life[pos] > 0 and dist<=bomb_blast_st[pos]-1: 
                min_life = int(bomb_life[pos])
            i -=1
        i=x
        while i < sz: 
            pos=(i,y)
            dist=abs(i-x)
            if utility.position_is_wall(board, pos):
                break
            if bomb_life[pos] > 0 and dist<=bomb_blast_st[pos]-1: 
                min_life = int(bomb_life[pos])
            i +=1
        j=y
        while j>=0: 
            pos=(x,j)
            dist=abs(j-y)
            if utility.position_is_wall(board, pos):
                break
            if bomb_life[pos] > 0 and dist<=bomb_blast_st[pos]-1: 
                min_life = int(bomb_life[pos])
            j -=1
        j=y
        while j < sz: 
            pos=(x,j)
            dist=abs(j-y)
            if utility.position_is_wall(board, pos):
                break
            if bomb_life[pos] > 0 and dist<=bomb_blast_st[pos]-1: 
                min_life = int(bomb_life[pos])
            j +=1
        return min_life

    bomb_real_life_map=np.zeros_like(board)
    sz=len(board)
    while True:
        no_change=[]
        for i in range(sz):
            for j in range(sz):
                if bomb_life[i,j]<1:
                    continue
                if bomb_life[i,j] <2:
                    real_life=1
                else:
                    real_life=bomb_real_life((i,j), board, bomb_blast_st, bomb_life)
                no_change.append((bomb_real_life_map[i,j] == real_life))
                bomb_real_life_map[i,j]=real_life
        if all(no_change):
            break
    return bomb_real_life_map

def get_next_step_flaming_positions(my_position, board, bomb_life, bomb_blast_st, enemies, teammate):
    def add_to_danger_positions(pos, danger_positions, board, blast_st, bomb_life, covered_bomb_positions):
        '''due to bombing chain, bombs with life>=2 would still blow up if they are in the danger positions '''
        sz=int(blast_st[pos])
        x,y=pos
        danger_positions.add(pos)
        for i in range(1,sz):
            pos2_list=[(x+i,y), (x-i,y), (x,y+i), (x,y-i)]
            for pos2 in pos2_list:
                if utility.position_on_board(board, pos2):
                    danger_positions.add(pos2)
                    if bomb_life[pos2]>1:
                        covered_bomb_positions.add(pos2)

    blast_st=bomb_blast_st
    all_other_agents=[e.value for e in enemies]+[teammate.value]
    #direction_list = [constants.Action.Left, constants.Action.Up, constants.Action.Right, constants.Action.Down]
    going_to_explode_bomb_positions=list(zip(*np.where(bomb_life == 1)))
    may_be_kicked=[]
    for pos in going_to_explode_bomb_positions:
        for direction in [constants.Action.Left, constants.Action.Up, constants.Action.Right, constants.Action.Down]:
            pos2 = utility.get_next_position(pos, direction)
            if not utility.position_on_board(board, pos2):
                continue
            if board[pos2] in all_other_agents:
                #mark to kicked
                #may_be_kicked.append(pos)
                break
    surely_danger_bomb_positions=[pos for pos in going_to_explode_bomb_positions if pos not in may_be_kicked]
    danger_positions=set()
    
    covered_bomb_positions=set()
    for pos in surely_danger_bomb_positions:
        add_to_danger_positions(pos, danger_positions, board, blast_st, bomb_life, covered_bomb_positions)

    all_covered=set()
    while len(covered_bomb_positions)>0:
        for pos in list(covered_bomb_positions):
            add_to_danger_positions(pos, danger_positions, board, blast_st, bomb_life, covered_bomb_positions)
            all_covered.add(pos)
            
        for pos in list(covered_bomb_positions):
            if pos in all_covered:
                covered_bomb_positions.remove(pos)
            
    #print('agent pos:', my_position, 'danger:', danger_positions) 
    return danger_positions

def is_in_corridor(board, position, perpendicular_dirs):
    d1=perpendicular_dirs[0]
    d2=perpendicular_dirs[1]
    p1=utility.get_next_position(position, d1)
    p2=utility.get_next_position(position, d2)

    con1=(not utility.position_on_board(board, p1) or not position_is_passable(board, p1))
    con2 = (not utility.position_on_board(board, p2) or not position_is_passable(board, p2))
    return con1 and con2

def agent_on_bomb_next_move_test(my_position, direction, board, bomb_life, blast_st):
    assert(bomb_life[my_position]>0)
    st=min(int(bomb_life[my_position]), int(blast_st[my_position]))
    pos=my_position
    perpendicular_dirs=[constants.Action.Left, constants.Action.Right] 
    if direction == constants.Action.Left or direction == constants.Action.Right:
        perpendicular_dirs=[constants.Action.Down, constants.Action.Up]
    
    corrdior_pos=[True]
    for i in range(st):
        next_pos=utility.get_next_position(pos, direction)
        if not utility.position_on_board(board, next_pos):
            break
        if not position_is_passable(board, next_pos):
            break
        if is_in_corridor(board, next_pos, perpendicular_dirs):
            corrdior_pos.append(True)
        else: corrdior_pos.append(False)
        pos=next_pos
    return not all(corrdior_pos)

def passable_may_next_to_enemy(board, position, enemies):
    #means enemy can get here in 2 steps thus block you!
    assert(position_is_passable(board, position, enemies)) 
    directions=[constants.Action.Left, constants.Action.Up, constants.Action.Right, constants.Action.Down]
    for direction in directions:
        next_pos = utility.get_next_position(position, direction)
        if not utility.position_on_board(board, next_pos):
            continue
        if utility.position_in_items(board, next_pos, enemies):
            return True
        #if position_is_passable(board, next_pos):
        #    for d2 in directions:
        #        next_pos2=utility.get_next_position(next_pos, direction)
        #    if not utility.position_on_board(board, next_pos2):
        #        continue
        #    if utility.position_in_items(board, next_pos2, enemies):
        #        return True
    return False 

def position_has_no_escape(obs, flame_positions, consider_enemy=False):
    directions=[constants.Action.Left, constants.Action.Up, constants.Action.Right, constants.Action.Down]
    my_position, can_kick, board, bomb_life, blast_st, enemies, teammate=obs['position'], \
    obs['can_kick'], obs['board'], obs['bomb_life'], obs['bomb_blast_strength'], obs['enemies'], obs['teammate']
    
    next_step_flaming_positions=get_next_step_flaming_positions(my_position, board, bomb_life, blast_st, enemies, teammate)
    future_flaming_positions=[] 
    for pos in list(zip(*np.where(bomb_life>0))):
        sz=int(blast_st[pos])
        x,y=pos
        future_flaming_positions.append(pos)
        for i in range(1,sz):
            pos2_list=[(x+i,y), (x-i,y), (x,y+i), (x,y-i)]
            for pos2 in pos2_list:
                if utility.position_on_board(board, pos2):
                    future_flaming_positions.append(pos2)

    valid_directions=[]
    num_passable=0
    passable_position=None
    
    for direction in directions:
        next_pos = utility.get_next_position(my_position, direction) 
        if not utility.position_on_board(board, next_pos):
            continue
        if can_kick and utility.position_in_items(board, next_pos, [constants.Item.Bomb]):
            if kick_test(board, blast_st, bomb_life, my_position, direction):
                #passed kick test, so at least kick direction is an escape
                return False
            continue
        flag_passable=position_is_passable(board, next_pos, enemies)
        if not flag_passable:
            continue
        elif flag_passable and consider_enemy and next_pos in future_flaming_positions and passable_may_next_to_enemy(board, next_pos, enemies):
            continue
        else:
            num_passable +=1
            passable_position=next_pos
        if next_pos in flame_positions or next_pos in next_step_flaming_positions:
            continue
        valid_directions.append(direction)
   
    if num_passable == 0:
        return True
    if (my_position not in flame_positions) and (my_position not in next_step_flaming_positions):
        return False
    return len(valid_directions)==0

def _position_will_be_flamed(board, position, bomb_life, bomb_blast_st, directions_to_check):
    for direction in directions_to_check:
        pos = utility.get_next_position(position, direction)
        k=1
        while utility.position_on_board(board, pos):
            if utility.position_is_wall(board, pos):
                break
            if bomb_life[pos]>0 and bomb_blast_st[pos]-1>=k:
                return True
            pos = utility.get_next_position(pos, direction)
            k +=1
    return False

def _opposite_direction(direction):
    if direction == constants.Action.Left:
        return constants.Action.Right
    if direction == constants.Action.Right:
        return constants.Action.Left
    if direction == constants.Action.Up:
        return constants.Action.Down
    if direction == constants.Action.Down:
        return constants.Action.Up

def position_is_passable(board, pos, enemies=[]):
    #hard code the smallest agent id on board
    if board[pos]>=10:
        return False 
    return utility.position_is_powerup(board, pos) or utility.position_is_passage(board, pos)

def agent_row_column_danger_positions(my_position, board, blast_st, bomb_life, enemies):
    #agent corridor bombs with life>=2 may also be dangerous due to terrain constraint
    #must be at least blast_strength - life away from the bomb
    ret=set()
    x,y=my_position
    if bomb_life[my_position]>0:
        #agent is on a bomb
        #special treatment 
        #--     --- 
        #   a_o 
        #--     ---
        danger_distance=max(blast_st[my_position] - bomb_life[my_position], 0)
        danger_distance=int(danger_distance)
        if bomb_life[my_position]<3:
            ret.add(my_position)
        '''
        bx,by=my_position[0], my_position[1]
        for i in range(x+1, x+danger_distance):
            pos=(i,y)
            pos1, pos2=(i,y+1), (i, y-1)
            if pos_is_wall_or_not_no_board(board, pos1) and pos_is_wall_or_not_no_board(board, pos2):
                ret.add(pos)
        for i in range(x-danger_distance, x):
            pos=(i,y)
            pos1, pos2=(i,y+1), (i, y-1)
            if pos_is_wall_or_not_no_board(board, pos1) and pos_is_wall_or_not_no_board(board, pos2):
                ret.add(pos)
        for j in range(y+1, y+danger_distance):
            pos=(x,j)
            pos1, pos2=(x-1, j), (x+1,j)
            if pos_is_wall_or_not_no_board(board, pos1) and pos_is_wall_or_not_no_board(board, pos2):
                ret.add(pos)
        for j in range(y-danger_distance, y):
            pos=(x,j)
            pos1, pos2=(x-1, j), (x+1,j)
            if pos_is_wall_or_not_no_board(board, pos1) and pos_is_wall_or_not_no_board(board, pos2):
                ret.add(pos)
        ret.add(my_position)
        '''
    
    v_bombs_up=[] #bombs at agent's column, vertical
    v_bombs_down=[] # vertical, down side
    h_bombs_left=[] #bombs at agent's row, horizontal 
    h_bombs_right=[] # horizontal, right side
   
    j=y
    while j>=0:
        pos=(x,j)
        if not position_is_passable(board, pos, enemies):
            break
        if bomb_life[pos] > 1:
            v_bombs_up.append(pos, abs(j-y))
        j -=1
    
    i=x
    while i>=0:
        pos=(i,y)
        if not position_is_passable(board, pos, enemies):
            break
        if bomb_life[pos] > 1:
            h_bombs_left.append(pos, abs(i-x))
        i -=1
      
    j=y
    while j < len(board):
        pos=(x,j)
        if not position_is_passable(board, pos, enemies):
            break
        if bomb_life[pos] > 1:
            v_bombs_down.append(pos, abs(j-y))
        j +=1
    i=x
    while i < len(board):
        pos=(i,y)
        if not position_is_passable(board, pos, enemies):
            break
        if bomb_life[pos] > 1:
            h_bombs_right.append(pos, abs(i-x))
        i +=1
    sz=len(board)
    for b in v_bombs_up:
        (bx,by),k=b
        assert(by < y and bx==x)
        for j in range(by+1, y):
            if j - by -1 > max(0, blast_st[(bx,by)] - bomb_life[(bx, by)]):
                break
            pos1, pos2=(x-1,j), (x+1, j)
            if not position_is_passable(board, pos1, enemies) and not position_is_passable(board, pos2, enemies):
                ret.add((x,j))
    for b in v_bombs_down:
        (bx,by),k=b
        assert(by > y and bx==x)
        for j in range(by-1, y, -1):
            if by - j -1 > max(0, blast_st[(bx,by)] - bomb_life[(bx, by)]):
                break
            pos1, pos2=(x-1,j), (x+1, j)
            if not position_is_passable(board, pos1, enemies) and not position_is_passable(board, pos2, enemies):
                ret.add((x,j))
    for b in h_bombs_left:
        (bx,by),k=b
        assert(bx < x and by==y)
        for i in range(bx+1, x):
            if i - bx -1 > max(0, blast_st[(bx,by)] - bomb_life[(bx, by)]):
                break
            pos1, pos2=(i,y-1), (i, y+1)
            if not position_is_passable(board, pos1, enemies) and not position_is_passable(board, pos2, enemies):
                ret.add((i,y))
    for b in h_bombs_right:
        (bx,by),k=b
        assert(bx > x and by==y)
        for i in range(bx-1, x, -1):
            if bx -i - 1 > max(0, blast_st[(bx,by)] - bomb_life[(bx, by)]):
                break
            pos1, pos2=(i,y-1), (i, y+1)
            if not position_is_passable(board, pos1, enemies) and not position_is_passable(board, pos2, enemies):
                ret.add((i,y))
    if len(ret)>0:
        print('v_h danger:', ret)
    return ret
