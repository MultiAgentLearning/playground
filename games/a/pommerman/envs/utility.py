from enum import Enum
import random

import numpy as np


RENDER_FPS = 10
BOARD_SIZE = 13 # Square map with this size
NUM_RIGID = 40
NUM_PASSAGE = 12
AGENT_VIEW_SIZE = 4 # How much of the map the agent sees not under fog of war.
TIME_LIMIT = 3000
HUMAN_FACTOR = 32
DEFAULT_BLAST_STRENGTH = 3
DEFAULT_BOMB_LIFE = 20
AGENT_COLORS = [[231,76,60], [46,139,87], [65,105,225], [238,130,238]] # color for each of the 4 agents
ITEM_COLORS = [[240,248,255], [128,128,128], [210,180,140], [255, 153, 51], None, None, [241, 196, 15], [141, 137, 124]]


class Items(Enum):
    PASSAGE = 0
    RIGID = 1
    WOOD = 2
    BOMB = 3 # prev was [19, 20, 24]
    ITEMEXTRA = 4
    ITEMBLAST = 5
    FLAMES = 6
    FOG = 7


class GameType(Enum):
    FFA = 1 # 1v1v1v1
    TEAM = 2 # 2v2 where each team can share observations. 
    TEAMDIFF = 3 # 2v2 where each team cannot share observations.
    TEAMDIFFCOMM = 4 # 2v2 where each cannot share observations but can pass a discrete communication.
    

class Direction(Enum):
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4


class Result(Enum):
    Win = 0
    Loss = 1
    Tie = 2
    Incomplete = 3


class InvalidDirection(Exception):
    pass


def make_board(size, num_rigid=None, num_passage=0):
    """Make the random but symmetric board.

    The numbers refer to:
     0 - passage
     1 - rigid wall
     2 - wood wall
     3 - bomb
     4 - extra bomb item (not implemented)
     5 - extra firepower item (not implemented)
     6 - current flames
     7 - fog of war.
     8 - 11: agents.

    Args:
      size: The dimension of the board, i.e. it's sizeXsize.

    Returns:
      board: The resulting random board.
    """
    # Initialize everything as a wood wall.
    board = 2 * np.ones((size, size)).astype(np.uint8)

    # Set the players down.
    board[1, 1] = 8
    board[size-2, 1] = 9
    board[1, size-2] = 10
    board[size-2, size-2] = 11

    # Give the players some breathing room on either side.
    for i in range(2, 4):
        board[1, i] = 0
        board[i, 1] = 0
        board[1, size-i-1] = 0
        board[size-i-1, 1] = 0
        board[size-2, size-i-1] = 0
        board[size-i-1, size-2] = 0
        board[size-2, i] = 0
        board[i, size-2] = 0

    if num_rigid == None:
        num_rigid = size

    while num_rigid > 0:
        row = random.randint(0, size-1)
        col = random.randint(0, size-1)
        if board[row, col] != 2:
            continue
        board[row, col] = 1
        num_rigid -= 1

    while num_passage > 0:
        row = random.randint(0, size-1)
        col = random.randint(0, size-1)
        if board[row, col] != 2:
            continue
        board[row, col] = 0
        num_passage -= 1

    return board


def is_valid_direction(board, position, direction):
    row, col = position

    if Direction(direction) == Direction.UP:
        return row - 1 >= 0 and board[row-1][col] in [0, 3]
    
    if Direction(direction) == Direction.DOWN:
        return row + 1 < len(board) and board[row+1][col] in [0, 3]
    
    if Direction(direction) == Direction.LEFT:
        return col - 1 >= 0 and board[row][col-1] in [0, 3]
    
    if Direction(direction) == Direction.RIGHT:
        return col + 1 < len(board[0]) and board[row][col+1] in [0, 3]

    raise InvalidDirection("We did not receive a valid direction.")


