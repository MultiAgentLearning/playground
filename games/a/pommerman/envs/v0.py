import numpy as np
from scipy.misc import imresize as resize
import time
from gym import spaces
from gym.utils import seeding
import gym

from . import utility


class Pomme(gym.Env):
    metadata = {
        'render.modes': ['human', 'rgb_array'],
        'video.frames_per_second' : utility.RENDER_FPS
    }

    def __init__(self,
                 game_type=None,
                 board_size=None,
                 num_rigid=None,
                 num_passage=None):
        self._agents = None
        self._game_type = game_type
        self._board_size = board_size
        self._num_rigid = num_rigid
        self._num_passage = num_passage
        self._viewer = None

        # Actions are: [Null, Up, Down, Left, Right, Bomb]
        self.action_space = spaces.Discrete(6)
        self.observation_space = spaces.Box(low=0, high=11, shape=(2, self._board_size, self._board_size))

    def set_agents(self, agents):
        self._agents = agents

    def act(self, obs):
        return [agent.act(obs[agent_id], action_space=self.action_space) for agent_id, agent in enumerate(self._agents)]

    def _get_observations(self):
        """Gets the observations as an np.array of the visible squares.

        The agent gets to choose whether it wants to keep the fogged part in memory.
        """
        agent_view_size = utility.AGENT_VIEW_SIZE
        observations = []
        for agent in self._agents:
            agent_obs = {}
            row, col = agent.position
            board = self._board.copy()
            for r in range(self._board_size):
                for c in range(self._board_size):
                    if not all([row >= r - agent_view_size, row < r + agent_view_size,
                                col >= c - agent_view_size, col < c + agent_view_size]):
                        board[r, c] = 7
            agent_obs['board'] = board
            agent_obs['position'] = (row, col)
            agent_obs['ammo'] = agent.ammo
            agent_obs['blast_strength'] = agent.blast_strength
            observations.append(agent_obs)
        return observations

    def _get_rewards(self):
        alive_agents = [num for num, agent in enumerate(self._agents) if agent.is_alive]
        if self._game_type == utility.GameType.FFA:
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

    def _get_done(self):
        alive = [agent for agent in self._agents if agent.is_alive]
        if self._game_type == utility.GameType.FFA:
            # TODO: Change back to 1.
            return len(alive) <= 0
        else:
            alive_ids = sorted([agent.agent_id for agent in alive])
            return any([
                len(alive_ids) <= 1,
                alive_ids == [0, 2],
                alive_ids == [1, 3],
            ])

    def _get_info(self):
        alive = [agent for agent in self._agents if agent.is_alive]
        if len(alive) == 0:
            return {'result': utility.Result.Tie}
        elif self._game_type == utility.GameType.FFA:
            if len(alive) == 1:
                return {'result': utility.Result.Win, 'winner': [alive[0].agent_id]}
            else:
                return {'result': utility.Result.Incomplete}
        else:
            alive_ids = sorted([agent.agent_id for agent in alive])
            if any([alive_ids == [0], alive_ids == [2], alive_ids == [0, 2]]):
                return {'result': utility.Result.Win, 'winner': [0, 2]}
            elif any([alive_ids == [1], alive_ids == [3], alive_ids == [1, 3]]):
                return {'result': utility.Result.Win, 'winner': [1, 3]}
            else:
                return {'result': utility.Result.Incomplete}

    def _reset(self):
        assert(self._agents is not None)

        self._board = utility.make_board(self._board_size, self._num_rigid, self._num_passage)
        self._bombs = []
        self._powerups = []
        for agent_id, agent in enumerate(self._agents):
            pos = np.where(self._board == agent_id+8)
            row = pos[0][0]
            col = pos[1][0]
            agent.set_start_position((row, col))
            agent.reset()

        return self._get_observations()

    def _seed(self, seed=None):
        gym.spaces.prng.seed(seed)
        self.np_random, seed = seeding.np_random(seed)
        return [seed]

    def _step(self, actions):
        # Replace the flames with passage
        self._board[np.where(self._board == utility.Items.FLAMES.value)] = 0

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
                elif utility.is_valid_direction(self._board, position, action):
                    agent.move(action)

        # Explode bombs.
        next_bombs = []
        exploded_map = np.zeros_like(self._board)
        for bomb in self._bombs:
            bomb.step()
            if bomb.exploded():
                bomb.bomber.incr_ammo()
                for _, indices in bomb.explode().items():
                    for r, c in indices:
                        if not all([r >= 0, c >= 0, r < self._board_size, c < self._board_size]):
                            break
                        if self._board[r][c] == 1:
                            break
                        exploded_map[r][c] = 1
                        if self._board[r][c] == 2:
                            break
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
                continue
                agent.die()
        exploded_map = np.array(exploded_map)

        # Update the board
        for bomb in self._bombs:
            self._board[bomb.position] = 3
        for agent in self._agents:
            self._board[np.where(self._board == agent.agent_id+8)] = 0
            if agent.is_alive:
                self._board[agent.position] = agent.agent_id+8
                
        self._board[np.where(exploded_map == 1)] = utility.Items.FLAMES.value

        done = self._get_done()
        obs = self._get_observations()
        reward = self._get_rewards()
        info = self._get_info()
        return obs, reward, done, info

    def _render_frames(self):
        agent_view_size = utility.AGENT_VIEW_SIZE
        frames = []

        all_frame = np.zeros((self._board_size, self._board_size, 3))
        for row in range(self._board_size):
            for col in range(self._board_size):
                if self._board[row][col] in list(range(8, 12)):
                    num_agent = self._board[row][col] - 8
                    if self._agents[num_agent].is_alive:
                        all_frame[row][col] = utility.AGENT_COLORS[num_agent]
                else:
                    all_frame[row][col] = utility.ITEM_COLORS[self._board[row][col]]

        all_frame = np.array(all_frame)
        frames.append(all_frame)

        for agent in self._agents:
            row, col = agent.position
            my_frame = all_frame.copy()
            for r in range(self._board_size):
                for c in range(self._board_size):
                    if not all([row >= r - agent_view_size, row < r + agent_view_size,
                                col >= c - agent_view_size, col < c + agent_view_size]):
                        my_frame[r, c] = utility.ITEM_COLORS[utility.Items.FOG.value]
            frames.append(my_frame)

        return frames

    def _render(self, mode='human', close=False):
        if close:
            if self._viewer is not None:
                self._viewer.close()
                self._viewer = None
            return

        human_factor = utility.HUMAN_FACTOR
        frames = self._render_frames()
        if mode == 'rgb_array':
            return frames[0] # just return the first value in this case.

        all_img = resize(frames[0], (self._board_size*human_factor, self._board_size*human_factor), interp='nearest')
        other_imgs = [
            resize(frame, (int(self._board_size*human_factor/4), int(self._board_size*human_factor/4)), interp='nearest')
            for frame in frames[1:]
        ]

        other_imgs = np.concatenate(other_imgs, 0)
        img = np.concatenate([all_img, other_imgs], 1)

        if self._viewer is None:
            from gym.envs.classic_control import rendering
            self._viewer = rendering.SimpleImageViewer()
        self._viewer.imshow(img)

        for agent in self._agents:
            if agent.has_key_input():
                self._viewer.window.on_key_press = agent.on_key_press
                self._viewer.window.on_key_release = agent.on_key_release
                break
        
        time.sleep(1.0 / utility.RENDER_FPS)
