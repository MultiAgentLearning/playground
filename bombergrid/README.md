# Bomber Grid World

Simplified version of Bomberman for multi-agent environment research competition.

Still early stage, but the multi-agent API is easy to understand.

Here is the code for random actions:

```
env = BomberGridEnv()
env.seed(0)

done = False
obs = env.reset()

while not done:

  env.render()

  actions = []
  for i in range(NUM_AGENTS):
    action = env.action_space.sample()
    actions.append(action)

  obs, reward, done, info = env.step(actions)
```

in the future, for other envs, might want to make observations an array of 4 different obs for each agent
