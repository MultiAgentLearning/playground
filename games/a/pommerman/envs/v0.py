from enum import Enum
import random
import sys, math
import numpy as np
# from skimage.transform import resize as resize
from scipy.misc import imresize as resize
import time
from gym import spaces
from gym.utils import seeding
import gym


RENDER_FPS = 10
BOARD_SIZE = 13 # Square map with this size
NUM_RIGID = 36
NUM_PASSAGE = 12
AGENT_VIEW_SIZE = 4 # How much of the map the agent sees not under fog of war.
TIME_LIMIT = 3000
HUMAN_FACTOR = 32
DEFAULT_BLAST_STRENGTH = 3
DEFAULT_BOMB_LIFE = 10
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


class InvalidDirection(Exception):
    pass


class Pomme(gym.Env):
    metadata = {
        'render.modes': ['human', 'rgb_array'],
        'video.frames_per_second' : RENDER_FPS
    }

    def __init__(self, game_type=GameType.FFA, board_size=BOARD_SIZE, num_rigid=NUM_RIGID,
                 num_passage=NUM_PASSAGE, on_key_press=None, on_key_release=None):
        self.num_agents = 4
        self._game_type = game_type
        self._board_size = board_size
        self._num_rigid = num_rigid
        self._num_passage = num_passage
        self._viewer = None
        self._on_key_press = on_key_press
        self._on_key_release = on_key_release

        # Actions are: [Null, Up, Down, Left, Right, Bomb]
        self.action_space = spaces.Discrete(6)
        self.observation_space = spaces.Box(low=0, high=11, shape=(2, self._board_size, self._board_size))

    def _get_observations(self):
        """Gets the observations as an np.array of the visible squares.

        The agent gets to choose whether it wants to keep the fogged part in memory.
        """
        observations = []
        for agent in self._agents:
            agent_obs = {}
            row, col = agent.position
            board = self._board.copy()
            for r in range(self._board_size):
                for c in range(self._board_size):
                    if not all([row >= r - AGENT_VIEW_SIZE, row < r + AGENT_VIEW_SIZE,
                                col >= c - AGENT_VIEW_SIZE, col < c + AGENT_VIEW_SIZE]):
                        board[r, c] = 7
            agent_obs['board'] = board
            agent_obs['position'] = (row, col)
            agent_obs['ammo'] = agent.ammo
            agent_obs['blast_strength'] = agent.blast_strength
            observations.append(agent_obs)
        return observations

    def _get_rewards(self):
        alive_agents = [num for num, agent in enumerate(self._agents) if agent.is_alive]
        if self._game_type == GameType.FFA:
            if len(alive_agents) == 1:
                ret = [-1]*4
                ret[alive_agents[0]] = 1
                return ret
            return [0]*4
        elif alive_agents == [0, 2] or alive_agents == [0] or alive_agents == [2]:
            return [1, -1, 1, -1]
        elif alive_agents == [1, 3] or alive_agents == [1] or alive_agents == [3]:
            return [-1, 1, -1, 1]
        else:
            return [0]*4

    def _reset(self):
        self._board = make_board(self._board_size, self._num_rigid, self._num_passage)
        self._bombs = []
        self._agents = []
        self._powerups = []
        for i in range(self.num_agents):
            agent_id = i+8
            pos = np.where(self._board == agent_id)
            row = pos[0][0]
            col = pos[1][0]
            self._agents.append(BomberAgent(agent_id, (pos[0][0], pos[1][0])))

        obs = self._get_observations()
        return obs

    def _seed(self, seed=None):
        gym.spaces.prng.seed(seed)
        self.np_random, seed = seeding.np_random(seed)
        return [seed]

    def _step(self, actions):
        # Replace the flames with passage
        self._board[np.where(self._board == Items.FLAMES.value)] = 0

        # Step the living agents.
        for num, agent in enumerate(self._agents):
            if agent.is_alive:
                action = actions[num]
                position = agent.position

                if action == 0:
                    continue
                elif action == 5:
                    bomb = agent.maybe_lay_bomb()
                    if bomb:
                        self._bombs.append(bomb)
                elif is_valid_direction(self._board, position, action):
                    agent.move(action)

        # Explode bombs.
        next_bombs = []
        exploded_map = np.zeros_like(self._board)
        for bomb in self._bombs:
            bomb.step()
            if bomb.exploded():
                bomb.bomber.incr_ammo()
                indices = bomb.explode()
                for r, c in indices:
                    if all([r >= 0, c >= 0, r < self._board_size, c < self._board_size]):
                        exploded_map[r][c] = 1
            else:
                next_bombs.append(bomb)

        # Remove bombs that were in the blast radius.
        self._bombs = []
        for bomb in next_bombs:
            if bomb.in_range(exploded_map):
                bomb.bomber.incr_ammo()
            else:
                self._bombs.append(bomb)

        # Kill these agents.
        for agent in self._agents:
            if agent.in_range(exploded_map):
                agent.die()
        exploded_map = np.array(exploded_map)

        # Update the board
        for bomb in self._bombs:
            self._board[bomb.position] = 3
        for agent in self._agents:
            self._board[np.where(self._board == agent.agent_id)] = 0
            self._board[agent.position] = agent.agent_id
        self._board[np.where(exploded_map == 1)] = Items.FLAMES.value

        num_alive = len([agent for agent in self._agents if agent.is_alive])
        done = num_alive <= 1
        obs = self._get_observations()
        reward = self._get_rewards()
        return obs, reward, done, {}

    def _render_frames(self):
        frames = []

        all_frame = np.zeros((self._board_size, self._board_size, 3))
        for row in range(self._board_size):
            for col in range(self._board_size):
                if self._board[row][col] in list(range(8, 12)):
                    num_agent = self._board[row][col] - 8
                    if self._agents[num_agent].is_alive:
                        all_frame[row][col] = AGENT_COLORS[num_agent]
                else:
                    all_frame[row][col] = ITEM_COLORS[self._board[row][col]]

        all_frame = np.array(all_frame)
        frames.append(all_frame)

        for agent in self._agents:
            row, col = agent.position
            my_frame = all_frame.copy()
            for r in range(self._board_size):
                for c in range(self._board_size):
                    if not all([row >= r - AGENT_VIEW_SIZE, row < r + AGENT_VIEW_SIZE,
                                col >= c - AGENT_VIEW_SIZE, col < c + AGENT_VIEW_SIZE]):
                        my_frame[r, c] = ITEM_COLORS[Items.FOG.value]
            frames.append(my_frame)

        return frames

    def _render(self, mode='human', close=False):
        if close:
            if self._viewer is not None:
                self._viewer.close()
                self._viewer = None
            return

        frames = self._render_frames()
        if mode == 'rgb_array':
            return frames[0] # just return the first value in this case.

        all_img = resize(frames[0], (self._board_size*HUMAN_FACTOR, self._board_size*HUMAN_FACTOR), interp='nearest')
        other_imgs = [
            resize(frame, (int(self._board_size*HUMAN_FACTOR/4), int(self._board_size*HUMAN_FACTOR/4)), interp='nearest')
            for frame in frames[1:]
        ]

        other_imgs = np.concatenate(other_imgs, 0)
        img = np.concatenate([all_img, other_imgs], 1)

        if self._viewer is None:
            from gym.envs.classic_control import rendering
            self._viewer = rendering.SimpleImageViewer()
        self._viewer.imshow(img)
        self._viewer.window.on_key_press = self._on_key_press
        self._viewer.window.on_key_release = self._on_key_release
        time.sleep(1.0 / RENDER_FPS)


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


class BomberAgent:
    """Container to keep the agent state."""
    def __init__(self, agent_id, position):
        self.agent_id = agent_id
        self.position = position
        self.ammo = 1
        self.is_alive = True
        self.blast_strength = DEFAULT_BLAST_STRENGTH

    def maybe_lay_bomb(self):
        if self.ammo > 0:
            self.ammo -= 1
            return Bomb(self, self.position, DEFAULT_BOMB_LIFE, self.blast_strength)
        return None

    def incr_ammo(self):
        self.ammo += 1

    def move(self, direction):
        row, col = self.position
        if Direction(direction) == Direction.UP:
            row -= 1
        elif Direction(direction) == Direction.DOWN:
            row += 1
        elif Direction(direction) == Direction.LEFT:
            col -= 1
        elif Direction(direction) == Direction.RIGHT:
            col += 1
        self.position = (row, col)

    def in_range(self, exploded_map):
        row, col = self.position
        return exploded_map[row][col] == 1

    def die(self):
        self.is_alive = False


class Bomb:
    def __init__(self, bomber, position, life, blast_strength):
        self.bomber = bomber
        self.position = position
        self._life = life
        self.blast_strength = blast_strength

    def step(self):
        self._life -= 1

    def exploded(self):
        return self._life == 0

    def explode(self):
        row, col = self.position
        indices = []
        indices.extend([row + i, col] for i in range(self.blast_strength))
        indices.extend([row - i, col] for i in range(1, self.blast_strength))
        indices.extend([row, col + i] for i in range(1, self.blast_strength))
        indices.extend([row, col - i] for i in range(1, self.blast_strength))
        return indices

    def in_range(self, exploded_map):
        row, col = self.position
        return exploded_map[row][col] == 1


if __name__=="__main__":
    # keyboard: player 1 is human
    from pyglet.window import key
    
    key_input = 0
  
    def on_key_press(k, mod):
        global key_input
        key_input = {
            key.UP: 1,
            key.DOWN: 2,
            key.LEFT: 3,
            key.RIGHT: 4,
            key.SPACE: 5,
            key.DELETE: 6,
        }.get(k)
        print("KI: ", key_input)

    def on_key_release(k, mod):
        global key_input
        key_input = 0

    env = PommeEnv(GameType.FFA, on_key_press=on_key_press, on_key_release=on_key_release)
    env.seed(np.random.randint(1000000))

    done = False
    obs = env.reset()

    while not done:
        env.render()
        actions = []
        if key_input == 6:
            time.sleep(50)
        actions.append(key_input)
        for i in range(1, env.num_agents):
            action = env.action_space.sample()
            actions.append(action)

        obs, reward, done, info = env.step(actions)

    env.render()
