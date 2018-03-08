"""The baseline Pommerman environment.

This evironment acts as game manager for Pommerman. Further environments, such as in v1.py, will inherit from this.
"""
from collections import defaultdict
import json
import os

import numpy as np
from scipy.misc import imresize as resize
import time
from gym import spaces
from gym.utils import seeding
import gym

from . import utility
from a.pommerman.characters import Flame
from a.pommerman.characters import Bomb

class Pomme(gym.Env):
    metadata = {
        'render.modes': ['human', 'rgb_array'],
    }

    def __init__(self,
                 render_fps=None,
                 game_type=None,
                 board_size=None,
                 agent_view_size=None,
                 num_rigid=None,
                 num_wood=None,
                 num_items=None,
                 max_steps=1000,
                 is_partially_observable=False,
                 **kwargs
    ):
        self._render_fps = render_fps
        self._agents = None
        self._game_type = game_type
        self._board_size = board_size
        self._agent_view_size = agent_view_size
        self._num_rigid = num_rigid
        self._num_wood = num_wood
        self._num_items = num_items
        self._max_steps = max_steps
        self._viewer = None
        self._is_partially_observable = is_partially_observable

        self.training_agent = None
        self.model = utility.ForwardModel()

        # Observation and Action Spaces. These are both geared towards a single agent even though the environment expects
        # actions and returns observations for all four agents. We do this so that it's clear what the actions and obs are
        # for a single agent. Wrt the observations, they are actually returned as a dict for easier understanding.

        self._set_action_space()
        self._set_observation_space()

    def _set_action_space(self):
        self.action_space = spaces.Discrete(6)

    def _set_observation_space(self):
        """The Observation Space for each agent.

        There are a total of 2*board_size^2+9 observations:
        - all of the board (board_size^2)
        - bomb blast strength (board_size^2).
        - agent's position (2)
        - num ammo (1)
        - blast strength (1)
        - can_kick (0 or 1)
        - teammate (one of {0, Agent.values}). If 0, then empty.
        - enemies (three of {0, Agent.values}). If 0, then empty.
        """
        min_obs = [0]*(2*self._board_size**2 + 9)
        max_obs = [len(utility.Item)]*self._board_size**2 + [10]*self._board_size**2 + [self._board_size]*2 + [10, 10, 1] + [3]*4
        self.observation_space = spaces.Box(np.array(min_obs), np.array(max_obs))

    def set_agents(self, agents):
        self._agents = agents

    def set_training_agent(self, agent_id):
        self.training_agent = agent_id

    def set_init_game_state(self, game_state_file):
        # game_state_file JSON format expected:
        # - list of agents serialized (agent_id, is_alive, position, ammo, blast_strength, can_kick)
        # - board matrix topology (board_size^2)
        # - board size
        # - list of bombs serialized (position, bomber_id, life, blast_strength, moving_direction)
        # - list of flames serialized (position, life)
        # - list of item by position
        # - step count
        self._init_game_state = None
        if game_state_file:
            with open(game_state_file, 'r') as f:
                self._init_game_state = json.loads(f.read())

    def has_training_agent(self):
        return self.training_agent is not None

    def make_board(self):
        self._board = utility.make_board(self._board_size, self._num_rigid, self._num_wood)

    def make_items(self):
        self._items = utility.make_items(self._board, self._num_items)

    def act(self, obs):
        agents = [agent for agent in self._agents if agent.agent_id != self.training_agent]
        return self.model.act(agents, obs, self.action_space)

    def get_observations(self):
        self.observations = self.model.get_observations(
            self._board, self._agents, self._bombs, self._is_partially_observable, self._agent_view_size)
        return self.observations

    def _get_rewards(self):
        return self.model.get_rewards(self._agents, self._game_type, self._step_count, self._max_steps)

    def _get_done(self):
        return self.model.get_done(self._agents, self._step_count, self._max_steps, self._game_type, self.training_agent)

    def _get_info(self, done, rewards):
        return self.model.get_info(done, rewards, self._game_type, self._agents)

    def reset(self):
        assert(self._agents is not None)

        if self._init_game_state is not None:
            self.set_json_info()
        else:
            self._step_count = 0
            self.make_board()
            self.make_items()
            self._bombs = []
            self._flames = []
            for agent_id, agent in enumerate(self._agents):
                pos = np.where(self._board == utility.agent_value(agent_id))
                row = pos[0][0]
                col = pos[1][0]
                agent.set_start_position((row, col))
                agent.reset()

        return self.get_observations()

    def seed(self, seed=None):
        gym.spaces.prng.seed(seed)
        self.np_random, seed = seeding.np_random(seed)
        return [seed]

    def step(self, actions):
        self._board, self._agents, self._bombs, self._items, self._flames = self.model.step(
            actions, self._board, self._agents, self._bombs, self._items, self._flames)

        done = self._get_done()
        obs = self.get_observations()
        reward = self._get_rewards()
        info = self._get_info(done, reward)

        self._step_count += 1
        return obs, reward, done, info

    def _render_frames(self):
        agent_view_size = utility.AGENT_VIEW_SIZE
        frames = []

        all_frame = np.zeros((self._board_size, self._board_size, 3))
        num_items = len(utility.Item)
        for row in range(self._board_size):
            for col in range(self._board_size):
                value = self._board[row][col]
                if utility.position_is_agent(self._board, (row, col)):
                    num_agent = value - num_items
                    if self._agents[num_agent].is_alive:
                        all_frame[row][col] = utility.AGENT_COLORS[num_agent]
                else:
                    all_frame[row][col] = utility.ITEM_COLORS[value]

        all_frame = np.array(all_frame)
        frames.append(all_frame)

        for agent in self._agents:
            row, col = agent.position
            my_frame = all_frame.copy()
            for r in range(self._board_size):
                for c in range(self._board_size):
                    if self._is_partially_observable and not all([
                            row >= r - agent_view_size, row < r + agent_view_size,
                            col >= c - agent_view_size, col < c + agent_view_size
                    ]):
                        my_frame[r, c] = utility.ITEM_COLORS[utility.Item.Fog.value]
            frames.append(my_frame)

        return frames

    def render(self, mode='human', close=False, record_pngs_dir=None, record_json_dir=None):
        from PIL import Image

        if close:
            if self._viewer is not None:
                self._viewer.close()
                self._viewer = None
            return

        if record_pngs_dir and not os.path.isdir(record_pngs_dir):
            os.makedirs(record_pngs_dir)

        human_factor = utility.HUMAN_FACTOR
        frames = self._render_frames()
        if mode == 'rgb_array':
            return frames[0]

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

        if record_pngs_dir:
            Image.fromarray(img).save(os.path.join(record_pngs_dir, '%d.png' % self._step_count))
        if record_json_dir:
            info = self.get_json_info()
            with open(os.path.join(record_json_dir, '%d.json' % self._step_count), 'w') as f:
                f.write(json.dumps(info, sort_keys=True, indent=4))

        for agent in self._agents:
            if agent.has_key_input():
                self._viewer.window.on_key_press = agent.on_key_press
                self._viewer.window.on_key_release = agent.on_key_release
                break

        time.sleep(1.0 / self._render_fps)

    @staticmethod
    def featurize(obs):
        board = obs["board"].reshape(-1).astype(np.float32)
        bombs = obs["bombs"].reshape(-1).astype(np.float32)
        position = utility.make_np_float(obs["position"])
        ammo = utility.make_np_float([obs["ammo"]])
        blast_strength = utility.make_np_float([obs["blast_strength"]])
        can_kick = utility.make_np_float([obs["can_kick"]])

        teammate = obs["teammate"]
        if teammate is not None:
            teammate = teammate.value
        else:
            teammate = -1
        teammate = utility.make_np_float([teammate])

        enemies = obs["enemies"]
        enemies = [e.value for e in enemies]
        if len(enemies) < 3:
            enemies = enemies + [-1]*(3 - len(enemies))
        enemies = utility.make_np_float(enemies)

        return np.concatenate((board, bombs, position, ammo, blast_strength, can_kick, teammate, enemies))

    def get_json_info(self):
        """Returns a json snapshot of the current game state."""
        ret = {
                'board_size': self._board_size,
                'step_count': self._step_count,
                'board': utility.to_json(self._board),
                'agents': utility.to_json(self._agents),
                'bombs': utility.to_json(self._bombs),
                'flames': utility.to_json(self._flames),
                'items': utility.to_json([[k, i] for k,i in self._items.items()])
            }

        return ret

    def set_json_info(self):
        """Sets the game state as the init_game_state."""
        self._step_count = self._init_game_state['step_count']
        self._board_size = self._init_game_state['board_size']

        boardArray = json.loads(self._init_game_state['board'])
        self._board = np.ones((self._board_size, self._board_size)).astype(np.uint8) * utility.Item.Passage.value
        for x in range(self._board_size):
            for y in range(self._board_size):
                self._board[x,y] = boardArray[x][y]

        self._items = {}
        itemArray = json.loads(self._init_game_state['items'])
        for i in itemArray:
            self._items[tuple(i[0])] = i[1]

        agentArray = json.loads(self._init_game_state['agents'])
        for a in agentArray:
            agent = next(x for x in self._agents if x.agent_id == a['agent_id'])
            agent.set_start_position((a['position'][0], a['position'][1]))
            agent.reset(a['ammo'], a['is_alive'], a['blast_strength'], a['can_kick'])
            
        self._bombs = []
        bombArray = json.loads(self._init_game_state['bombs'])
        for b in bombArray:
            bomber = next(x for x in self._agents if x.agent_id == b['bomber_id'])
            self._bombs.append(Bomb(bomber, tuple(b['position']), b['life'], b['blast_strength'], b['moving_direction']))

        self._flames = []
        flameArray = json.loads(self._init_game_state['flames'])
        for f in flameArray:
            self._flames.append(Flame(tuple(f['position']), f['life']))
        
