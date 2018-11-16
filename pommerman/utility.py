'''This file contains a set of utility functions that
help with positioning, building a game board, and
encoding data to be used later'''
import itertools
import json
import random
import os
import copy
from jsonmerge import Merger

from gym import spaces
import numpy as np

import constants


class PommermanJSONEncoder(json.JSONEncoder):
    '''A helper class to encode state data into a json object'''
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, constants.Item):
            return obj.value
        elif isinstance(obj, constants.Action):
            return obj.value
        elif isinstance(obj, np.int64):
            return int(obj)
        elif hasattr(obj, 'to_json'):
            return obj.to_json()
        elif isinstance(obj, spaces.Discrete):
            return obj.n
        elif isinstance(obj, spaces.Tuple):
            return [space.n for space in obj.spaces]
        return json.JSONEncoder.default(self, obj)


def make_board(size, num_rigid=0, num_wood=0):
    """Make the random but symmetric board.

    The numbers refer to the Item enum in constants. This is:
     0 - passage
     1 - rigid wall
     2 - wood wall
     3 - bomb
     4 - flames
     5 - fog
     6 - extra bomb item
     7 - extra firepower item
     8 - kick
     9 - skull
     10 - 13: agents

    Args:
      size: The dimension of the board, i.e. it's sizeXsize.
      num_rigid: The number of rigid walls on the board. This should be even.
      num_wood: Similar to above but for wood walls.

    Returns:
      board: The resulting random board.
    """

    def lay_wall(value, num_left, coordinates, board):
        '''Lays all of the walls on a board'''
        x, y = random.sample(coordinates, 1)[0]
        coordinates.remove((x, y))
        coordinates.remove((y, x))
        board[x, y] = value
        board[y, x] = value
        num_left -= 2
        return num_left

    def make(size, num_rigid, num_wood):
        '''Constructs a game/board'''
        # Initialize everything as a passage.
        board = np.ones((size,
                         size)).astype(np.uint8) * constants.Item.Passage.value

        # Gather all the possible coordinates to use for walls.
        coordinates = set([
            (x, y) for x, y in \
            itertools.product(range(size), range(size)) \
            if x != y])

        # Set the players down. Exclude them from coordinates.
        # Agent0 is in top left. Agent1 is in bottom left.
        # Agent2 is in bottom right. Agent 3 is in top right.
        board[1, 1] = constants.Item.Agent0.value
        board[size - 2, 1] = constants.Item.Agent1.value
        board[size - 2, size - 2] = constants.Item.Agent2.value
        board[1, size - 2] = constants.Item.Agent3.value
        agents = [(1, 1), (size - 2, 1), (1, size - 2), (size - 2, size - 2)]
        for position in agents:
            if position in coordinates:
                coordinates.remove(position)

        # Exclude breathing room on either side of the agents.
        for i in range(2, 4):
            coordinates.remove((1, i))
            coordinates.remove((i, 1))
            coordinates.remove((1, size - i - 1))
            coordinates.remove((size - i - 1, 1))
            coordinates.remove((size - 2, size - i - 1))
            coordinates.remove((size - i - 1, size - 2))
            coordinates.remove((i, size - 2))
            coordinates.remove((size - 2, i))

        # Lay down wooden walls providing guaranteed passage to other agents.
        wood = constants.Item.Wood.value
        for i in range(4, size - 4):
            board[1, i] = wood
            board[size - i - 1, 1] = wood
            board[size - 2, size - i - 1] = wood
            board[size - i - 1, size - 2] = wood
            coordinates.remove((1, i))
            coordinates.remove((size - i - 1, 1))
            coordinates.remove((size - 2, size - i - 1))
            coordinates.remove((size - i - 1, size - 2))
            num_wood -= 4

        # Lay down the rigid walls.
        while num_rigid > 0:
            num_rigid = lay_wall(constants.Item.Rigid.value, num_rigid,
                                 coordinates, board)

        # Lay down the wooden walls.
        while num_wood > 0:
            num_wood = lay_wall(constants.Item.Wood.value, num_wood,
                                coordinates, board)

        return board, agents

    assert (num_rigid % 2 == 0)
    assert (num_wood % 2 == 0)
    board, agents = make(size, num_rigid, num_wood)

    # Make sure it's possible to reach most of the passages.
    while len(inaccessible_passages(board, agents)) > 4:
        board, agents = make(size, num_rigid, num_wood)

    return board


def make_items(board, num_items):
    '''Lays all of the items on the board'''
    item_positions = {}
    while num_items > 0:
        row = random.randint(0, len(board) - 1)
        col = random.randint(0, len(board[0]) - 1)
        if board[row, col] != constants.Item.Wood.value:
            continue
        if (row, col) in item_positions:
            continue

        item_positions[(row, col)] = random.choice([
            constants.Item.ExtraBomb, constants.Item.IncrRange,
            constants.Item.Kick
        ]).value
        num_items -= 1
    return item_positions


def inaccessible_passages(board, agent_positions):
    """Return inaccessible passages on this board."""
    seen = set()
    agent_position = agent_positions.pop()
    passage_positions = np.where(board == constants.Item.Passage.value)
    positions = list(zip(passage_positions[0], passage_positions[1]))

    Q = [agent_position]
    while Q:
        row, col = Q.pop()
        for (i, j) in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            next_position = (row + i, col + j)
            if next_position in seen:
                continue
            if not position_on_board(board, next_position):
                continue
            if position_is_rigid(board, next_position):
                continue

            if next_position in positions:
                positions.pop(positions.index(next_position))
                if not len(positions):
                    return []

            seen.add(next_position)
            Q.append(next_position)
    return positions


def is_valid_direction(board, position, direction, invalid_values=None):
    '''Determins if a move is in a valid direction'''
    row, col = position
    if invalid_values is None:
        invalid_values = [item.value for item in \
                          [constants.Item.Rigid, constants.Item.Wood]]

    if constants.Action(direction) == constants.Action.Stop:
        return True

    if constants.Action(direction) == constants.Action.Up:
        return row - 1 >= 0 and board[row - 1][col] not in invalid_values

    if constants.Action(direction) == constants.Action.Down:
        return row + 1 < len(board) and board[row +
                                              1][col] not in invalid_values

    if constants.Action(direction) == constants.Action.Left:
        return col - 1 >= 0 and board[row][col - 1] not in invalid_values

    if constants.Action(direction) == constants.Action.Right:
        return col + 1 < len(board[0]) and \
            board[row][col+1] not in invalid_values

    raise constants.InvalidAction("We did not receive a valid direction: ",
                                  direction)


def _position_is_item(board, position, item):
    '''Determins if a position holds an item'''
    return board[position] == item.value


def position_is_flames(board, position):
    '''Determins if a position has flames'''
    return _position_is_item(board, position, constants.Item.Flames)


def position_is_bomb(bombs, position):
    """Check if a given position is a bomb.
    
    We don't check the board because that is an unreliable source. An agent
    may be obscuring the bomb on the board.
    """
    for bomb in bombs:
        if position == bomb.position:
            return True
    return False


def position_is_powerup(board, position):
    '''Determins is a position has a powerup present'''
    powerups = [
        constants.Item.ExtraBomb, constants.Item.IncrRange, constants.Item.Kick
    ]
    item_values = [item.value for item in powerups]
    return board[position] in item_values


def position_is_wall(board, position):
    '''Determins if a position is a wall tile'''
    return position_is_rigid(board, position) or \
        position_is_wood(board, position)


def position_is_passage(board, position):
    '''Determins if a position is passage tile'''
    return _position_is_item(board, position, constants.Item.Passage)


def position_is_rigid(board, position):
    '''Determins if a position has a rigid tile'''
    return _position_is_item(board, position, constants.Item.Rigid)


def position_is_wood(board, position):
    '''Determins if a position has a wood tile'''
    return _position_is_item(board, position, constants.Item.Wood)


def position_is_agent(board, position):
    '''Determins if a position has an agent present'''
    return board[position] in [
        constants.Item.Agent0.value, constants.Item.Agent1.value,
        constants.Item.Agent2.value, constants.Item.Agent3.value
    ]


def position_is_enemy(board, position, enemies):
    '''Determins if a position is an enemy'''
    return constants.Item(board[position]) in enemies


# TODO: Fix this so that it includes the teammate.
def position_is_passable(board, position, enemies):
    '''Determins if a possible can be passed'''
    return all([
        any([
            position_is_agent(board, position),
            position_is_powerup(board, position),
            position_is_passage(board, position)
        ]), not position_is_enemy(board, position, enemies)
    ])


def position_is_fog(board, position):
    '''Determins if a position is fog'''
    return _position_is_item(board, position, constants.Item.Fog)


def agent_value(id_):
    '''Gets the state value based off of agents "name"'''
    return getattr(constants.Item, 'Agent%d' % id_).value


def position_in_items(board, position, items):
    '''Dtermines if the current positions has an item'''
    return any([_position_is_item(board, position, item) for item in items])


def position_on_board(board, position):
    '''Determines if a positions is on the board'''
    x, y = position
    return all([len(board) > x, len(board[0]) > y, x >= 0, y >= 0])


def get_direction(position, next_position):
    """Get the direction such that position --> next_position.

    We assume that they are adjacent.
    """
    x, y = position
    next_x, next_y = next_position
    if x == next_x:
        if y < next_y:
            return constants.Action.Right
        else:
            return constants.Action.Left
    elif y == next_y:
        if x < next_x:
            return constants.Action.Down
        else:
            return constants.Action.Up
    raise constants.InvalidAction(
        "We did not receive a valid position transition.")


def get_next_position(position, direction):
    '''Returns the next position coordinates'''
    x, y = position
    if direction == constants.Action.Right:
        return (x, y + 1)
    elif direction == constants.Action.Left:
        return (x, y - 1)
    elif direction == constants.Action.Down:
        return (x + 1, y)
    elif direction == constants.Action.Up:
        return (x - 1, y)
    elif direction == constants.Action.Stop:
        return (x, y)
    raise constants.InvalidAction("We did not receive a valid direction.")


def make_np_float(feature):
    '''Converts an integer feature space into a floats'''
    return np.array(feature).astype(np.float32)


def join_json_state(record_json_dir, agents, finished_at, config, info):
    '''Combines all of the json state files into one'''
    json_schema = {"properties": {"state": {"mergeStrategy": "append"}}}
    
    json_template = {
        "agents": agents,
        "finished_at": finished_at,
        "config": config,
        "result": {
            "name": info['result'].name,
            "id": info['result'].value
        }
    }

    if info['result'] is not constants.Result.Tie:
        json_template['winners'] = info['winners']

    json_template['state'] = []

    merger = Merger(json_schema)
    base = merger.merge({}, json_template)

    for root, dirs, files in os.walk(record_json_dir):
        for name in files:
            path = os.path.join(record_json_dir, name)
            if name.endswith('.json') and "game_state" not in name:
                with open(path) as data_file:
                    data = json.load(data_file)
                    head = {"state": [data]}
                    base = merger.merge(base, head)

    with open(os.path.join(record_json_dir, 'game_state.json'), 'w') as f:
        f.write(json.dumps(base, sort_keys=True, indent=4))

    for root, dirs, files in os.walk(record_json_dir):
        for name in files:
            if "game_state" not in name:
                os.remove(os.path.join(record_json_dir, name))


def softmax(x):
    x = np.array(x)
    x -= np.max(x, axis=-1, keepdims=True)  # For numerical stability
    exps = np.exp(x)
    return exps / np.sum(exps, axis=-1, keepdims=True)


def update_agent_memory(cur_memory, cur_obs):
    """
    Update agent's memory of the board
    :param cur_memory: Current memory including board, bomb_life, and bomb_blast_strength
    :param cur_obs: Current observation of the agent, including the above
    :return: The new memory
    """
    def _get_explosion_range(row, col, blast_strength_map):
        strength = int(blast_strength_map[row, col])
        indices = {
            'up': ([row - i, col] for i in range(1, strength)),
            'down': ([row + i, col] for i in range(strength)),
            'left': ([row, col - i] for i in range(1, strength)),
            'right': ([row, col + i] for i in range(1, strength))
        }
        return indices

    # Note: all three 11x11 boards are numpy arrays
    if cur_memory is None:
        new_memory = {
            'bomb_life': np.copy(cur_obs['bomb_life']),
            'bomb_blast_strength': np.copy(cur_obs['bomb_blast_strength']),
            'board': np.copy(cur_obs['board'])
        }
        return new_memory

    # Work on a copy and keep original unchanged
    cur_memory = copy.deepcopy(cur_memory)

    # Update history by incrementing timestep by 1
    board = cur_memory['board']
    bomb_life = cur_memory['bomb_life']
    bomb_blast_strength = cur_memory['bomb_blast_strength']

    # Decrease bomb_life by 1
    original_bomb_life = np.copy(bomb_life)
    np.putmask(bomb_life, bomb_life > 0, bomb_life - 1)

    # Find out which bombs are going to explode
    exploding_bomb_pos = np.logical_xor(original_bomb_life, bomb_life)
    non_exploding_bomb_pos = np.logical_and(bomb_life, np.ones_like(bomb_life))
    has_explosions = exploding_bomb_pos.any()

    # Map to record which positions will become flames
    flamed_positions = np.zeros_like(board)

    while has_explosions:
        has_explosions = False
        # For each bomb
        for row, col in zip(*exploding_bomb_pos.nonzero()):
            # For each direction
            for direction, indices in _get_explosion_range(row, col, bomb_blast_strength).items():
                # For each location along that direction
                for r, c in indices:
                    if not position_on_board(board, (r, c)):
                        break
                    # Stop when reaching a wall
                    if board[r, c] == constants.Item.Rigid.value:
                        break
                    # Otherwise the position is flamed
                    flamed_positions[r, c] = 1
                    # Stop when reaching a wood
                    if board[r, c] == constants.Item.Wood.value:
                        break

        # Check if other non-exploding bombs are triggered
        exploding_bomb_pos = np.zeros_like(exploding_bomb_pos)

        for row, col in zip(*non_exploding_bomb_pos.nonzero()):
            if flamed_positions[row, col]:
                has_explosions = True
                exploding_bomb_pos[row, col] = True
                non_exploding_bomb_pos[row, col] = False


    new_memory = dict()

    # Update bomb_life map
    new_memory['bomb_life'] = np.where(flamed_positions == 0, bomb_life, 0)
    # Update bomb_strength map
    new_memory['bomb_blast_strength'] = np.where(flamed_positions == 0, bomb_blast_strength, 0)

    # Update Board
    # If board from observation has fog value, do nothing &
    # keep original updated history.
    # Otherwise, overwrite history by observation.
    new_memory['board'] = np.where(flamed_positions == 0, cur_memory['board'], constants.Item.Passage.value)

    # Overlay agent's newest observations onto the memory
    obs_board = cur_obs['board']
    for r, c in zip(*np.where(obs_board != constants.Item.Fog.value)):
        # board[r, c] = obs_board[r, c] if obs_board[r, c] in self.memory_values else 0
        new_memory['board'][r, c] = obs_board[r, c]
        new_memory['bomb_life'][r, c] = cur_obs['bomb_life'][r, c]
        new_memory['bomb_blast_strength'][r, c] = cur_obs['bomb_blast_strength'][r, c]

    # For invisible parts of the memory, only keep useful information
    for r, c in zip(*np.where(obs_board == constants.Item.Fog.value)):
        if new_memory['board'][r, c] not in constants.MEMORY_VALS:
            new_memory['board'][r, c] = constants.Item.Passage.value

    return new_memory


def combine_agent_obs_and_memory(memory, cur_obs):
    """
    Returns an extended observation of the agent
    by incorporating its memory.
    NOTE: Assumes the memory is up-to-date (i.e. called `update_agent_memory()`)
    :param memory: The agent's memory of the game, including board, bomb life, and blast strength
    :param cur_obs: The agent's current observation object
    :return: The new, extended observation
    """
    if memory is None:
        return cur_obs

    extended_obs = copy.deepcopy(cur_obs)
    for map in ['bomb_life', 'bomb_blast_strength', 'board']:
        extended_obs[map] = np.copy(memory[map])
    return extended_obs

    

def convert_to_model_input(agent_id, history):
    # History Observation
    board_obs = history['board']
    bomb_blast_strength_obs = history['bomb_blast_strength']
    bomb_life_obs = history['bomb_life']

    # Model Input
    passage_input = np.zeros([11,11])
    wall_input = np.zeros([11,11])
    wood_input = np.zeros([11,11])
    self_input = np.zeros([11,11])
    friend_input = np.zeros([11,11])
    enemy_input = np.zeros([11,11])
    flame_input = np.zeros([11,11])
    extra_bomb_input = np.zeros([11,11])
    increase_range_input = np.zeros([11,11])
    kick_input = np.zeros([11,11])
    fog_input = np.zeros([11,11])
    can_kick_input = np.zeros([11,11])
    self_ammo_input = np.zeros([11,11])

    passage_input[board_obs==0] = 1
    wall_input[board_obs==1] = 1
    wood_input[board_obs==2] = 1
    self_input[board_obs==agent_id+10] = 1
    friend_input[board_obs == (agent_id+2)%4 + 10] = 1
    enemy_input[board_obs == (agent_id+1)%4 + 10] = 1
    enemy_input[board_obs == (agent_id+3)%4 + 10] = 1
    flame_input[board_obs==4] = 1
    extra_bomb_input[board_obs==6] = 1
    increase_range_input[board_obs==7] = 1
    kick_input[board_obs==8] = 1
    fog_input[board_obs==5] = 1

    if history['can_kick']:
        can_kick_input = np.ones([11,11])

    self_blast_strength_input = np.full((11,11), history['blast_strength'])
    self_ammo_input = np.full((11,11), history['ammo'])

    bomb_input = get_bomb_input(bomb_blast_strength_obs, bomb_life_obs, board_obs)

    # Stack Inputs
    model_input = []
    model_input.append(passage_input)
    model_input.append(wall_input)
    model_input.append(wood_input)
    model_input.append(bomb_input)
    model_input.append(flame_input)
    model_input.append(fog_input)
    model_input.append(extra_bomb_input)
    model_input.append(increase_range_input)
    model_input.append(kick_input)
    model_input.append(can_kick_input)
    model_input.append(self_blast_strength_input)
    model_input.append(self_ammo_input)
    model_input.append(self_input)
    model_input.append(friend_input)
    model_input.append(enemy_input)

    return np.array(model_input)


def get_bomb_input(bomb_blast_strength_obs, bomb_life_obs, board_obs):
    bomb_input = np.zeros([11,11])
    bomb_set = {}
    for i in range(10,0,-1):
        bomb_x_list, bomb_y_list = np.where(bomb_life_obs==i)
        for j in range(len(bomb_x_list)):
            bomb_x = bomb_x_list[j]
            bomb_y = bomb_y_list[j]
            strength = bomb_blast_strength_obs[bomb_x, bomb_y]
            life = bomb_life_obs[bomb_x, bomb_y]
            bomb_set[(bomb_x,bomb_y)] = (strength, life)
            bomb_expand(bomb_input, (bomb_x,bomb_y), strength, life, bomb_set, board_obs)
    return bomb_input


def bomb_expand(bomb_input, bomb_pos, strength, life, bomb_set, board_obs):
    bomb_x, bomb_y = bomb_pos
    bomb_input[bomb_x, bomb_y] = life

    # Up Expand
    bomb_expand_direction(bomb_input, bomb_pos, strength, life, bomb_set, board_obs, (-1, 0))

    # Down Expand
    bomb_expand_direction(bomb_input, bomb_pos, strength, life, bomb_set, board_obs, (1, 0))

    # Left Expand
    bomb_expand_direction(bomb_input, bomb_pos, strength, life, bomb_set, board_obs, (0, -1))

    # Right Expand
    bomb_expand_direction(bomb_input, bomb_pos, strength, life, bomb_set, board_obs, (0, 1))


def bomb_expand_direction(bomb_input, bomb_pos, strength, life, bomb_set, board_obs, direction):
    bomb_x, bomb_y = bomb_pos
    for i in range(1, int(strength)):
        bomb_new_x = bomb_x + i * direction[0]
        bomb_new_y = bomb_y + i * direction[1]

        if bomb_new_x < 0 or bomb_new_x >= bomb_input.shape[0]:
            break
        if bomb_new_y < 0 or bomb_new_y >= bomb_input.shape[1]:
            break

        if board_obs[bomb_new_x, bomb_new_y] == 1:
            break
        elif board_obs[bomb_new_x, bomb_new_y] == 2:
            bomb_input[bomb_new_x, bomb_new_y] = life
            break
        elif bomb_input[bomb_new_x, bomb_new_y] > life or bomb_input[bomb_new_x, bomb_new_y] == 0:
            bomb_input[bomb_new_x, bomb_new_y] = life
            if (bomb_new_x, bomb_new_y) in bomb_set:
                old_bomb_strength = bomb_set[(bomb_new_x, bomb_new_y)][0]
                bomb_expand(bomb_input, (bomb_new_x, bomb_new_y), old_bomb_strength, life, bomb_set, board_obs)
