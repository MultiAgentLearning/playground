"""The set of constants in the game.

This includes not just ints but also classes like Item, GameType, Action, etc.
"""
from enum import Enum

RENDER_FPS = 15
BOARD_SIZE = 11
NUM_RIGID = 36
NUM_WOOD = 36
NUM_ITEMS = 20
BOARD_SIZE_ONE_VS_ONE = 8
NUM_RIGID_ONE_VS_ONE = 16
NUM_WOOD_ONE_VS_ONE = 16
NUM_ITEMS_ONE_VS_ONE = 10
AGENT_VIEW_SIZE = 4
HUMAN_FACTOR = 32
DEFAULT_BLAST_STRENGTH = 2
DEFAULT_BOMB_LIFE = 9
# color for each of the 4 agents
AGENT_COLORS = [[231, 76, 60], [46, 139, 87], [65, 105, 225], [238, 130, 238]]
# color for each of the items.
ITEM_COLORS = [[240, 248, 255], [128, 128, 128], [210, 180, 140],
               [255, 153, 51], [241, 196, 15], [141, 137, 124]]
ITEM_COLORS += [(153, 153, 255), (153, 204, 204), (97, 169, 169), (48, 117,
                                                                   117)]
# If using collapsing boards, the step at which the board starts to collapse.
FIRST_COLLAPSE = 500
MAX_STEPS = 800
RADIO_VOCAB_SIZE = 8
RADIO_NUM_WORDS = 2

# Files for images and and fonts
RESOURCE_DIR = 'resources/'
FILE_NAMES = [
    'Passage', 'Rigid', 'Wood', 'Bomb', 'Flames', 'Fog', 'ExtraBomb',
    'IncrRange', 'Kick', 'AgentDummy', 'Agent0', 'Agent1', 'Agent2', 'Agent3',
    'AgentDummy-No-Background', 'Agent0-No-Background', 'Agent1-No-Background',
    'Agent2-No-Background', 'Agent3-No-Background', 'X-No-Background',
    'Agent0-Team', 'Agent1-Team', 'Agent2-Team', 'Agent3-Team',
    'Agent0-Team-No-Background', 'Agent1-Team-No-Background', 
    'Agent2-Team-No-Background', 'Agent3-Team-No-Background',
]
IMAGES_DICT = {
    num: {
        'id': num,
        'file_name': '%s.png' % file_name,
        'name': file_name,
        'image': None
    } for num, file_name in enumerate(FILE_NAMES)
}
BOMB_FILE_NAMES = [
    'Bomb-1', 'Bomb-2', 'Bomb-3', 'Bomb-4', 'Bomb-5', 'Bomb-6',
    'Bomb-7', 'Bomb-8', 'Bomb-9', 'Bomb-10',
]
BOMB_DICT = {
    num: {
        'id': num,
        'file_name': '%s.png' % file_name,
        'name': file_name,
        'image': None
    } for num, file_name in enumerate(BOMB_FILE_NAMES)
}
FONTS_FILE_NAMES = ['Cousine-Regular.ttf']

# Human view board configurations
BORDER_SIZE = 20
MARGIN_SIZE = 10
TILE_SIZE = 50
BACKGROUND_COLOR = (41, 39, 51, 255)
TILE_COLOR = (248, 221, 82, 255)
TEXT_COLOR = (170, 170, 170, 255)


class Item(Enum):
    """The Items in the game.

    When picked up:
      - ExtraBomb increments the agent's ammo by 1.
      - IncrRange increments the agent's blast strength by 1.
      - Kick grants the agent the ability to kick items.

    AgentDummy is used by team games to denote the third enemy and by ffa to
    denote the teammate.
    """
    Passage = 0
    Rigid = 1
    Wood = 2
    Bomb = 3
    Flames = 4
    Fog = 5
    ExtraBomb = 6
    IncrRange = 7
    Kick = 8
    AgentDummy = 9
    Agent0 = 10
    Agent1 = 11
    Agent2 = 12
    Agent3 = 13


class GameType(Enum):
    """The Game Types.

    FFA: 1v1v1v1. Submit an agent; it competes against other submitted agents.
    Team: 2v2. Submit an agent; it is matched up randomly with another agent
      and together take on two other similarly matched agents.
    TeamRadio: 2v2. Submit two agents; they are matched up against two other
      agents. Each team passes discrete communications to each other.
    OneVsOne: 1v1. A research environment for dueling between two agents
    """
    FFA = 1
    Team = 2
    TeamRadio = 3
    OneVsOne = 4


class Action(Enum):
    '''The Actions an agent can take'''
    Stop = 0
    Up = 1
    Down = 2
    Left = 3
    Right = 4
    Bomb = 5


class Result(Enum):
    '''The results available for the end of the game'''
    Win = 0
    Loss = 1
    Tie = 2
    Incomplete = 3


class InvalidAction(Exception):
    '''Invalid Actions Exception'''
    pass
