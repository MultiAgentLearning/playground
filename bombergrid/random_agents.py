'''
all four players are random action
'''
import numpy as np
from bomber_grid import BomberGridEnv

env = BomberGridEnv()
env.seed(np.random.randint(1000000))
done = False
obs = env.reset()

while not done:

  env.render()

  actions = []
  for i in range(env.num_agents):
    action = env.action_space.sample()
    actions.append(action)

  obs, reward, done, info = env.step(actions)

  # in the future, for other envs, might want to make observations
  # an array of different obs for each agent, since each agent might
  # see a unique observation tailored to it.

env.render()
print('final result:', info)
