'''
Bomber Grid World

Simplified version of Bomberman for multi-agent environment research competition.

'''

import sys, math
import numpy as np
from scipy.misc import imresize as resize
import time

import gym
from gym import spaces
from gym.utils import seeding

# settings

SCREEN_SIZE = 13 # assume square maps
TIME_LIMIT = 3000
HUMAN_FACTOR = 40
RENDER_FPS = 10
DEFAULT_BLAST_STRENGTH = 3
BOMB_LIFE = 20
NUM_AGENTS = 4

# 0 - passage
# 1 - rigid wall
# 2 - wood wall
# 3 - bomb
# 4 - extra bomb item (not implemented)
# 5 - extra firepower item (not implemented)
INIT_MAP = [
1,1,1,1,1,1,1,1,1,1,1,1,1,
1,0,0,0,2,2,2,2,0,0,0,0,1,
1,0,1,2,1,2,1,2,1,2,1,0,1,
1,0,2,2,2,2,2,2,2,2,2,0,1,
1,0,1,2,1,2,1,2,1,2,1,2,1,
1,2,2,2,2,2,2,2,2,2,2,2,1,
1,2,1,2,1,2,1,2,1,2,1,2,1,
1,2,2,2,2,2,2,2,2,2,2,2,1,
1,2,1,2,1,2,1,2,1,2,1,0,1,
1,0,2,2,2,2,2,2,2,2,2,0,1,
1,0,1,2,1,2,1,2,1,2,1,0,1,
1,0,0,0,0,2,2,2,2,0,0,0,1,
1,1,1,1,1,1,1,1,1,1,1,1,1
]

INIT_POSITION = [
0,0,0,0,0,0,0,0,0,0,0,0,0,
0,1,0,0,0,0,0,0,0,0,0,3,0,
0,0,0,0,0,0,0,0,0,0,0,0,0,
0,0,0,0,0,0,0,0,0,0,0,0,0,
0,0,0,0,0,0,0,0,0,0,0,0,0,
0,0,0,0,0,0,0,0,0,0,0,0,0,
0,0,0,0,0,0,0,0,0,0,0,0,0,
0,0,0,0,0,0,0,0,0,0,0,0,0,
0,0,0,0,0,0,0,0,0,0,0,0,0,
0,0,0,0,0,0,0,0,0,0,0,0,0,
0,0,0,0,0,0,0,0,0,0,0,0,0,
0,2,0,0,0,0,0,0,0,0,0,4,0,
0,0,0,0,0,0,0,0,0,0,0,0,0
]

ITEM_COLOR=[[240,248,255], [128,128,128], [210,180,140], [19,20,24]] # color for each of the 5 items

EXPLOSION_COLOR = [241,196,15]

AGENT_COLOR=[[231,76,60], [46,139,87], [65,105,225], [238,130,238]] # color for each of the 4 agents

class BomberAgent:
  '''
  This is not the AI, but just a container to keep the state of the agent
  '''
  def __init__(self, agent_id, row, col):
    self.id = agent_id
    self.col = col
    self.row = row
    self.ammo = 1
    self.alive = True
    self.blast_strength = DEFAULT_BLAST_STRENGTH
  def bomb_action(self, obs, bomb_array):
    element = obs[0, self.row, self.col]
    if self.ammo > 0 and element == 0: # can place bombs on passage ways
      self.ammo -= 1
      obs[0, self.row, self.col] = 3 # place bomb
      bomb_array.append(Bomb(self))
  def step(self, action, obs, bomb_array):
    if action == 5: # bomb key
      self.bomb_action(obs, bomb_array)
      return
    dir_row = 0
    dir_col = 0
    if action == 1: # up
      dir_row = -1
    elif action == 2: # down 
      dir_row = 1
    elif action == 3: # left
      dir_col = -1
    elif action == 4: # right
      dir_col = 1
    element = obs[0, self.row+dir_row, self.col+dir_col]
    if (element != 1 and element != 2 and element != 3): # not rigid wall or wood or bomb
      self.row += dir_row
      self.col += dir_col

class Bomb:
  def __init__(self, agent):
    self.agent = agent
    self.row = agent.row
    self.col = agent.col
    self.life = BOMB_LIFE
    self.explode = False
    self.blast_strength = self.agent.blast_strength
  def step(self, obs, bomb_array, explosion_map):
    self.life -= 1
    if self.life < 0 and self.explode == False:
      self.explode = True
      self.agent.ammo += 1
    if self.explode:
      obs[0, self.row, self.col] = 0
      explosion_map[self.row, self.col] = 1

      for direction in range(4):
        dir_row = 0
        dir_col = 0
        if direction == 0: # up
          dir_row = -1
        elif direction == 1: # down 
          dir_row = 1
        elif direction == 2: # left
          dir_col = -1
        elif direction == 3: # right
          dir_col = 1
        for k in range(self.blast_strength):
          row = self.row+dir_row*k
          col = self.col+dir_col*k
          element = obs[0, row, col]
          if element != 1: # if it is not a wall, blow it up
            explosion_map[row, col] = 1
            obs[0, row, col] = 0
          if element != 0:
            break

class BomberGridEnv(gym.Env):
  metadata = {
    'render.modes': ['human', 'rgb_array'],
    'video.frames_per_second' : RENDER_FPS
  }

  def __init__(self):
    self._viewer = None
    self.action_space = spaces.Discrete(6) # do nothing, up, down, left, right, bomb
    self.observation_space = spaces.Box(low=0, high=255, shape=(2, SCREEN_SIZE, SCREEN_SIZE))

    self.num_agents = NUM_AGENTS

    self._obs = np.zeros((2, SCREEN_SIZE, SCREEN_SIZE)).astype(np.uint8)
    self._obs[0] = np.resize(INIT_MAP, (SCREEN_SIZE, SCREEN_SIZE))
    self._obs[1] = np.resize(INIT_POSITION, (SCREEN_SIZE, SCREEN_SIZE))

    self._agents = []
    self._bombs = []

    for i in range(NUM_AGENTS):
      agent_id = i+1
      pos = np.where(self._obs[1] == agent_id)
      row = pos[0][0]
      col = pos[1][0]
      self._agents.append(BomberAgent(agent_id, row, col))

    self._explosion = np.zeros((SCREEN_SIZE, SCREEN_SIZE)).astype(np.uint8)
    self._frame = np.zeros((SCREEN_SIZE, SCREEN_SIZE, 3)).astype(np.uint8)
    #self._seed()

  def _place_agents_on_obs(self):
    self._obs[1] = np.zeros((SCREEN_SIZE, SCREEN_SIZE)).astype(np.uint8)
    for i in range(NUM_AGENTS):
      agent_id = i+1
      row = self._agents[i].row
      col = self._agents[i].col
      self._obs[1,row,col] = i+1

  def _clear_random_wood(self):
    # get rid of a fourth of the wooden walls randomly
    for row in range(SCREEN_SIZE):
      for col in range(SCREEN_SIZE):
        element = self._obs[0, row, col]
        if element == 2: # if it is wood wall
          if self.np_random.choice([0, 1, 2, 3]) == 0:
            self._obs[0, row, col] = 0 # clear the wooden wall

  def _reset(self):
    #self._clear_random_wood()
    return self._obs

  def _seed(self, seed=None):
    gym.spaces.prng.seed(seed)
    self.np_random, seed = seeding.np_random(seed)
    return [seed]

  def _step(self, actions):
    self._explosion = np.zeros((SCREEN_SIZE, SCREEN_SIZE)).astype(np.uint8)
    done = True
    # return game info (ie who is still alove) before executing this step
    info = [0] * NUM_AGENTS
    for i in range(NUM_AGENTS):
      agent = self._agents[i]
      if agent.alive:
        info[i] = 1
    info = np.array(info)
    info = info / np.maximum(1.0, np.sum(info)) # normalization
    for i in range(NUM_AGENTS):
      agent = self._agents[i]
      if agent.alive:
        agent.step(actions[i], self._obs, self._bombs)
    for bomb in self._bombs:
      bomb.step(self._obs, self._bombs, self._explosion)
    # garbage collection
    bombs = []
    for bomb in self._bombs:
      if not bomb.explode:
        bombs.append(bomb)
    self._bombs = bombs
    # make bombs explode if they were hit by fire
    for bomb in self._bombs:
      if self._explosion[bomb.row, bomb.col] != 0:
        bomb.explode = True
    # make agents die if they got in the cross fire
    for agent in self._agents:
      if self._explosion[agent.row, agent.col] != 0:
        agent.alive = False
    self._place_agents_on_obs()
    # check for done
    for i in range(NUM_AGENTS):
      agent = self._agents[i]
      if agent.alive:
        done = False
    return self._obs, 0, done, info

  def _render_frame(self):
    for row in range(SCREEN_SIZE):
      for col in range(SCREEN_SIZE):
        c = ITEM_COLOR[self._obs[0][row][col]]
        self._frame[row, col, 0] = c[0]
        self._frame[row, col, 1] = c[1]
        self._frame[row, col, 2] = c[2]
    for i in range(NUM_AGENTS):
      if self._agents[i].alive:
        c = AGENT_COLOR[i]
        row = self._agents[i].row
        col = self._agents[i].col
        self._frame[row, col, 0] = c[0]
        self._frame[row, col, 1] = c[1]
        self._frame[row, col, 2] = c[2]
    for row in range(SCREEN_SIZE):
      for col in range(SCREEN_SIZE):
        if self._explosion[row][col] == 1:
          c = EXPLOSION_COLOR
          self._frame[row, col, 0] = c[0]
          self._frame[row, col, 1] = c[1]
          self._frame[row, col, 2] = c[2]

  def _render(self, mode='human', close=False):
    if close:
      if self._viewer is not None:
        self._viewer.close()
        self._viewer = None
      return

    self._render_frame() # compiles observation space into RGB frames for display purpose.

    if mode == 'rgb_array':
      return self._frame

    # assume human mode
    img = resize(self._frame, (SCREEN_SIZE*HUMAN_FACTOR, SCREEN_SIZE*HUMAN_FACTOR), interp='nearest')
    if self._viewer is None:
      from gym.envs.classic_control import rendering
      self._viewer = rendering.SimpleImageViewer()
    self._viewer.imshow(img)
    time.sleep(1.0 / RENDER_FPS)

if __name__=="__main__":

  # keyboard: player 1 is human
  from pyglet.window import key

  key_input = 0

  def key_press(k, mod):
    global key_input
    if k==key.SPACE: key_input = 5
    if k==key.LEFT:  key_input = 3
    if k==key.RIGHT: key_input = 4
    if k==key.UP:    key_input = 1
    if k==key.DOWN:  key_input = 2

  def key_release(k, mod):
    global key_input
    key_input = 0

  env = BomberGridEnv()
  env.seed(np.random.randint(1000000))

  done = False
  obs = env.reset()

  env.render()
  env._viewer.window.on_key_press = key_press
  env._viewer.window.on_key_release = key_release

  while not done:

    env.render()

    actions = []
    actions.append(key_input)
    for i in range(1, env.num_agents):
      action = env.action_space.sample()
      actions.append(action)

    obs, reward, done, info = env.step(actions)

  env.render()
  print('final result:', info)
