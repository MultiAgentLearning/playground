from collections import defaultdict
from enum import Enum
import itertools
import random

import numpy as np


RENDER_FPS = 15
BOARD_SIZE = 13 # Square map with this size
NUM_RIGID = 50
NUM_WOOD = 50
NUM_ITEMS = 16
AGENT_VIEW_SIZE = 5 # How much of the map the agent sees not under fog of war.
TIME_LIMIT = 3000
HUMAN_FACTOR = 32
DEFAULT_BLAST_STRENGTH = 3
DEFAULT_BOMB_LIFE = 25
AGENT_COLORS = [[231,76,60], [46,139,87], [65,105,225], [238,130,238]] # color for each of the 4 agents
ITEM_COLORS = [[240,248,255], [128,128,128], [210,180,140], [255, 153, 51], [241, 196, 15], [141, 137, 124]]
# NOTE: This is for the ExtraBomb, IncrRange, etc. 
ITEM_COLORS += [(153, 153, 255), (153, 204, 204), (97, 169, 169), (48, 117, 117)]
FIRST_COLLAPSE = 500 # The first step at which the board starts to collapse.
MAX_STEPS = 2500


class Items(Enum):
    Passage = 0
    Rigid = 1
    Wood = 2
    Bomb = 3
    Flames = 4
    Fog = 5
    ExtraBomb = 6 # adds ammo.
    IncrRange = 7 # increases the blast_strength
    Kick = 8 # can kick bombs by touching them.
    Skull = 9 # randomly either reduces ammo (capped at 1) or blast_strength (capped at 2)


class GameType(Enum):
    # 1v1v1v1. You submit an agent and it competes against other single agents.
    FFA = 1 
    # 2v2: You submit two agents and they compete together against other teams.
    Team = 2
    # 2v2: Same as `Team` but additionally the agents pass discrete communications to each other.
    TeamRadio = 3

    
class Direction(Enum):
    Up = 1
    Down = 2
    Left = 3
    Right = 4


class Result(Enum):
    Win = 0
    Loss = 1
    Tie = 2
    Incomplete = 3


class InvalidDirection(Exception):
    pass


def make_board(size, num_rigid=0, num_wood=0):
    """Make the random but symmetric board.

    The numbers refer to the Items enum in utility. This is:
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
    assert(num_rigid % 2 == 0)
    assert(num_wood % 2 == 0)

    def lay_wall(value, num_left):
        x, y = random.sample(coordinates, 1)[0]
        coordinates.remove((x, y))
        coordinates.remove((y, x))
        board[x, y] = value
        board[y, x] = value
        num_left -= 2
        return num_left

    if num_rigid is None:
        num_rigid = size
    _num_rigid = num_rigid
    _num_wood = num_wood

    # Initialize everything as a passage.
    board = np.ones((size, size)).astype(np.uint8) * Items.Passage.value

    # Gather all the possible coordinates to use for walls.
    coordinates = set([(x, y) for x, y in itertools.product(range(size), range(size)) if x != y])

    # Set the players down. Exclude them from coordinates.
    num_first_agent = len(Items)
    board[1, 1] = num_first_agent
    board[size-2, 1] = num_first_agent + 1
    board[1, size-2] = num_first_agent + 2
    board[size-2, size-2] = num_first_agent + 3
    agents = [(1, 1), (size-2, 1), (1, size-2), (size-2, size-2)]
    for position in agents:
        if position in coordinates:
            coordinates.remove(position)

    # Exclude breathing room on either side of the agents.
    for i in range(2, 4):
        coordinates.remove((1, i))
        coordinates.remove((i, 1))
        coordinates.remove((1, size-i-1))
        coordinates.remove((size-i-1, 1))
        coordinates.remove((size-2, size-i-1))
        coordinates.remove((size-i-1, size-2))
        coordinates.remove((i, size-2))
        coordinates.remove((size-2, i))

    # Lay down the rigid walls.
    while num_rigid > 0:
        num_rigid = lay_wall(Items.Rigid.value, num_rigid)

    # Lay down the wooden walls.
    while num_wood > 0:
        num_wood = lay_wall(Items.Wood.value, num_wood)

    # Make sure it's possible for the agents to reach each other.
    if not is_accessible(board, agents):
        print('not accessible, rerunning')
        return make_board(size, _num_rigid, _num_wood)

    return board


def make_items(board, num_items):
    item_positions = {}
    while num_items > 0:
        row = random.randint(0, len(board)-1)
        col = random.randint(0, len(board[0])-1)
        if board[row, col] != Items.Wood.value:
            continue
        if (row, col) in item_positions:
            continue

        item_positions[(row, col)] = random.randint(Items.Fog.value + 1, len(Items) + 1)
        num_items -= 1
    return item_positions


def is_accessible(board, agent_positions):
    """Return true if all of the agents can reach each other."""
    seen = set()
    agent_position = agent_positions.pop()
    Q = [agent_position]
    while Q:
        row, col = Q.pop()
        for (i, j) in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            next_row = row+i
            next_col = col+j
            if (next_row, next_col) in seen:
                continue
            if next_row < 0 or next_row >= len(board) or next_col < 0 or next_col >= len(board):
                continue
            if board[next_row, next_col] == 1:
                continue

            if (next_row, next_col) in agent_positions:
                agent_positions.pop(agent_positions.index((next_row, next_col)))
                if not len(agent_positions):
                    return True

            seen.add((next_row, next_col))
            Q.append((next_row, next_col))
    return False
    

def is_valid_direction(board, position, direction, invalid_values=None):
    row, col = position
    invalid_values = invalid_values or [item.value for item in [Items.Rigid, Items.Wood]]

    if Direction(direction) == Direction.Up:
        return row - 1 >= 0 and board[row-1][col] not in invalid_values
    
    if Direction(direction) == Direction.Down:
        return row + 1 < len(board) and board[row+1][col] not in invalid_values
    
    if Direction(direction) == Direction.Left:
        return col - 1 >= 0 and board[row][col-1] not in invalid_values

    if Direction(direction) == Direction.Right:
        return col + 1 < len(board[0]) and board[row][col+1] not in invalid_values

    raise InvalidDirection("We did not receive a valid direction.")


def is_item(board, position):
    item_values = [
        item.value for item in [Items.ExtraBomb, Items.IncrRange, Items.Kick, Items.Skull]
    ]
    return board[position] in item_values
        

def is_bomb(board, position):
    return board[position] == Items.Bomb.value
