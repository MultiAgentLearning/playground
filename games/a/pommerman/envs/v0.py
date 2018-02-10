from collections import defaultdict
import os

import numpy as np
from scipy.misc import imresize as resize
import time
from gym import spaces
from gym.utils import seeding
import gym

from . import utility
from a.pommerman.characters import Flame


class Pomme(gym.Env):
    metadata = {
        'render.modes': ['human', 'rgb_array'],
        'video.frames_per_second' : utility.RENDER_FPS
    }

    def __init__(self,
                 game_type=None,
                 board_size=None,
                 agent_view_size=None,
                 num_rigid=None,
                 num_wood=None,
                 num_items=None,
                 max_steps=1000,
    ):
        self._agents = None
        self._game_type = game_type
        self._board_size = board_size
        self._agent_view_size = agent_view_size
        self._num_rigid = num_rigid
        self._num_wood = num_wood
        self._num_items = num_items
        self._max_steps = max_steps
        self._viewer = None

        # Observation and Action Spaces. These are both geared towards a single agent even though the environment expects
        # actions and returns observations for all four agents. We do this so that it's clear what the actions and obs are
        # for a single agent. Wrt the observations, they are actually returned as a dict for easier understanding.
        self.action_space = spaces.Discrete(6)
        # Observations: This is geared towards a single agent.
        self.observation_space = spaces.Box(low=0, high=len(utility.Item), shape=(self._board_size, self._board_size))

    def set_agents(self, agents):
        self._agents = agents

    def act(self, obs):
        ret = []
        for agent in self._agents:
            if agent.is_alive:
                action = agent.act(obs[agent.agent_id], action_space=self.action_space)
                if agent.agent_id == 0 and action == 6:
                    time.sleep(300)
                ret.append(action)
            else:
                ret.append(utility.Action.Stop)
        return ret

    def _get_observations(self):
        """Gets the observations as an np.array of the visible squares.

        The agent gets to choose whether it wants to keep the fogged part in memory.
        """
        attrs = ['position', 'ammo', 'blast_strength', 'can_kick', 'speed',
                 'acceleration', 'max_speed', 'teammate', 'enemies']
        keys = ['board'] + attrs

        agent_view_size = self._agent_view_size
        observations = []
        for agent in self._agents:
            agent_obs = {}
            board = self._board.copy()
            for row in range(self._board_size):
                for col in range(self._board_size):
                    if not self._in_view_range(agent.position, row, col):
                        board[row, col] = utility.Item.Fog.value
            agent_obs['board'] = board
            agent_obs['bombs'] = self._get_bombs_in_range(agent.position)
            for attr in attrs:
                assert hasattr(agent, attr)
                agent_obs[attr] = getattr(agent, attr)
            observations.append(agent_obs)

        return observations

    def _get_rewards(self):
        alive_agents = [num for num, agent in enumerate(self._agents) if agent.is_alive]
        if self._game_type == utility.GameType.FFA:
            ret = [-1]*4
            if len(alive_agents) == 1 or self._step_count >= self._max_steps:
                for num in alive_agents:
                    ret[num] = 1
            else:
                for num in alive_agents:
                    ret[num] = 0
            return ret
        elif alive_agents == [0, 2] or alive_agents == [0] or alive_agents == [2]:
            return [1, -1, 1, -1]
        elif alive_agents == [1, 3] or alive_agents == [1] or alive_agents == [3]:
            return [-1, 1, -1, 1]
        elif self._step_count >= self._max_steps:
            return [1]*4
        else:
            return [0]*4

    def _get_done(self):
        alive = [agent for agent in self._agents if agent.is_alive]
        alive_ids = sorted([agent.agent_id for agent in alive])
        if self._game_type == utility.GameType.FFA:
            return len(alive) <= 1
        elif any([
                len(alive_ids) <= 1,
                alive_ids == [0, 2],
                alive_ids == [1, 3],
        ]):
            return True
        else:
            return self._step_count >= self._max_steps

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

    def reset(self):
        assert(self._agents is not None)

        self._step_count = 0
        self._board = utility.make_board(self._board_size, self._num_rigid, self._num_wood)
        self._items = utility.make_items(self._board, self._num_items)
        self._bombs = []
        self._flames = []
        self._powerups = []
        for agent_id, agent in enumerate(self._agents):
            pos = np.where(self._board == utility.agent_value(agent_id+1))
            row = pos[0][0]
            col = pos[1][0]
            agent.set_start_position((row, col))
            agent.reset()

        ret = self._get_observations()
        return ret

    def seed(self, seed=None):
        gym.spaces.prng.seed(seed)
        self.np_random, seed = seeding.np_random(seed)
        return [seed]

    def step(self, actions):
        # Tick the flames. Replace any dead ones with passages. If there is an item there, then reveal that item.
        flames = []
        for flame in self._flames:
            position = flame.position
            if flame.is_dead():
                item_value = self._items.get(position)
                if item_value:
                    del self._items[position]
                else:
                    item_value = utility.Item.Passage.value
                self._board[position] = item_value
            else:
                flame.tick()
                flames.append(flame)
        self._flames = flames

        # Step the living agents.
        # If two agents try to go to the same spot, they should bounce back to their previous spots.
        # This is a little complicated because what if there are three agents all in a row.
        # If the one in the middle tries to go to the left and bounces with the one on the left,
        # and then the one on the right tried to go to the middle one's position, she should also bounce.
        # A way of doing this is to gather all the new positions before taking any actions.
        # Then, if there are disputes, correct those disputes iteratively.
        def make_counter(next_positions):
            counter = defaultdict(list)
            for num, next_position in enumerate(next_positions):
                if next_position is not None:
                    counter[next_position].append(num)
            return counter

        def has_position_conflict(counter):
            return any([len(agent_ids) > 1 for next_position, agent_ids in counter.items() if next_position])

        curr_positions = [agent.position for agent in self._agents]
        next_positions = [agent.position for agent in self._agents]
        for agent, action in zip(self._agents, actions):
            if agent.is_alive:
                position = agent.position

                if action == utility.Action.Stop.value:
                    agent.stop()
                elif action == utility.Action.Bomb.value:
                    bomb = agent.maybe_lay_bomb()
                    if bomb:
                        self._bombs.append(bomb)
                elif utility.is_valid_direction(self._board, position, action):
                    next_position = agent.get_next_position(action)

                    # This might be a bomb position. Only move in that case if the agent can kick.
                    if not utility.position_is_bomb(self._board, next_position):
                        next_positions[agent.agent_id] = next_position
                    elif not agent.can_kick:
                        agent.stop()
                    else:
                        next_positions[agent.agent_id] = next_position
                else:
                    # The agent made an invalid direction.
                    agent.stop()
            else:
                next_positions.append(None)

        counter = make_counter(next_positions)
        while has_position_conflict(counter):
            for next_position, agent_ids in counter.items():
                if next_position and len(agent_ids) > 1:
                    for agent_id in agent_ids:
                        next_positions[agent_id] = curr_positions[agent_id]
            counter = make_counter(next_positions)

        for agent, curr_position, next_position, direction in zip(self._agents, curr_positions, next_positions, actions):
            if curr_position != next_position:
                agent.move(direction)
                if agent.can_kick:
                    bombs = [bomb for bomb in self._bombs if bomb.position == agent.position]
                    if bombs:
                        bombs[0].moving_direction = utility.Action(direction)

            if utility.position_is_powerup(self._board, agent.position):
                agent.pick_up(utility.Item(self._board[agent.position]))
                self._board[agent.position] = utility.Item.Passage.value

        # Explode bombs.
        next_bombs = []
        exploded_map = np.zeros_like(self._board)
        for bomb in self._bombs:
            bomb.tick()
            if bomb.is_moving():
                invalid_values = list(range(len(utility.Item)+1))[1:]
                if utility.is_valid_direction(self._board, bomb.position, bomb.moving_direction.value, invalid_values=invalid_values):
                    self._board[bomb.position] = utility.Item.Passage.value
                    bomb.move()
                else:
                     bomb.stop()

            if bomb.exploded():
                bomb.bomber.incr_ammo()
                for _, indices in bomb.explode().items():
                    for r, c in indices:
                        if not all([r >= 0, c >= 0, r < self._board_size, c < self._board_size]):
                            break
                        if self._board[r][c] == utility.Item.Rigid.value:
                            break
                        exploded_map[r][c] = 1
                        if self._board[r][c] == utility.Item.Wood.value:
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
                agent.die()
        exploded_map = np.array(exploded_map)

        # Update the board
        for bomb in self._bombs:
            self._board[bomb.position] = utility.Item.Bomb.value

        for agent in self._agents:
            self._board[np.where(self._board == utility.agent_value(agent.agent_id+1))] = utility.Item.Passage.value
            if agent.is_alive:
                self._board[agent.position] = utility.agent_value(agent.agent_id+1)

        flame_positions = np.where(exploded_map == 1)
        for row, col in zip(flame_positions[0], flame_positions[1]):
            self._flames.append(Flame((row, col)))
        for flame in self._flames:
            self._board[flame.position] = utility.Item.Flames.value

        done = self._get_done()
        obs = self._get_observations()
        reward = self._get_rewards()
        info = self._get_info()
        self._step_count += 1

        if hasattr(self, 'collapses'):
            for ring, collapse in enumerate(self.collapses):
                if self._step_count == collapse:
                    self._board = self._collapse_board(ring)
                    break

        return obs, reward, done, info

    def _in_view_range(self, position, vrow, vcol):
        agent_view_size = self._agent_view_size
        row, col = position
        return all([row >= vrow - agent_view_size, row < vrow + agent_view_size,
                    col >= vcol - agent_view_size, col < vcol + agent_view_size])

    def _get_bombs_in_range(self, position):
        bombs = []
        agent_view_size = self._agent_view_size
        for bomb in self._bombs:
            vrow, vcol = bomb.position
            if self._in_view_range(position, vrow, vcol):
                bombs.append({'position': bomb.position, 'blast_strength': bomb.blast_strength})
        return bombs

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
                    if not all([row >= r - agent_view_size, row < r + agent_view_size,
                                col >= c - agent_view_size, col < c + agent_view_size]):
                        my_frame[r, c] = utility.ITEM_COLORS[utility.Item.Fog.value]
            frames.append(my_frame)

        return frames

    def render(self, mode='human', close=False, record_dir=None):
        from PIL import Image

        if close:
            if self._viewer is not None:
                self._viewer.close()
                self._viewer = None
            return

        if record_dir and not os.path.isdir(record_dir):
            os.makedirs(record_dir)

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
        if record_dir:
            Image.fromarray(img).save(os.path.join(record_dir, '%d.png' % self._step_count))

        for agent in self._agents:
            if agent.has_key_input():
                self._viewer.window.on_key_press = agent.on_key_press
                self._viewer.window.on_key_release = agent.on_key_release
                break

        time.sleep(1.0 / utility.RENDER_FPS)
