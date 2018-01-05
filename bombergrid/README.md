# Bomber Grid World

Simplified version of Bomberman for multi-agent environment research competition.

Still early stage, but the multi-agent API is easy to understand.

Here is the code for random actions:

```
from bomber_grid import BomberGridEnv

env = BomberGridEnv()
env.seed(0)

done = False
obs = env.reset()

while not done:

  env.render()

  actions = []
  for i in range(env.num_agents):
    action = env.action_space.sample()
    actions.append(action)

  obs, reward, done, info = env.step(actions)

env.render()
print('final result:', info)
```

In the future, for other envs, might want to make observations an array of different obs for each agent, since each agent might see a unique observation tailored to it.

To run the version where Player 1 is keyboard player (up down left right space):

```
python bomber_grid.py
```

To run the version where all agents are just a random action agent (i.e. the sample code above):

```
python random_agents.py
```
