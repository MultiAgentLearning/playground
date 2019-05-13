# Getting Started
## Pre-requisites
* [Python 3.6.0](https://www.python.org/downloads/release/python-360/)+ (including `pip`)
* [Docker](https://www.docker.com/) (only needed for `DockerAgent`)
* [virtualenv](https://virtualenv.pypa.io/en/stable/) (optional, for isolated Python environment)
## Installation
* Clone the repository
```
$ git clone https://github.com/MultiAgentLearning/playground ~/playground
```
## Pip
* **OPTIONAL**: Setup an isolated virtual Python environment by running the following commands
```
$ virtualenv ~/venv
```
This environment needs to be activated for usage. Any package installations will now persist
in this virtual environment folder only.
```
source ~/venv/bin/activate
```
* Install the `pommerman` package. This needs to be done every time the code is updated to get the
latest modules
```
$ cd ~/playground
$ pip install -U .
```
## Conda
* Install the `pommerman` environment.
```
$ cd ~/playground
$ conda env create -f env.yml
$ conda activate pommerman
```
* To update the environment
```
$ conda env update -f env.yml --prune
```
## Examples
### Free-For-All
The code below runs a sample Free-For-All game with two **SimpleAgent**'s and two **RandomAgent**'s on the board.  
```python
#!/usr/bin/python
"""A simple Free-For-All game with Pommerman."""
import pommerman
from pommerman import agents


def main():
    """Simple function to bootstrap a game"""
    # Print all possible environments in the Pommerman registry
    print(pommerman.REGISTRY)

    # Create a set of agents (exactly four)
    agent_list = [
        agents.SimpleAgent(),
        agents.RandomAgent(),
        agents.SimpleAgent(),
        agents.RandomAgent(),
        # agents.DockerAgent("pommerman/simple-agent", port=12345),
    ]
    # Make the "Free-For-All" environment using the agent list
    env = pommerman.make('PommeFFACompetition-v0', agent_list)

    # Run the episodes just like OpenAI Gym
    for i_episode in range(1):
        state = env.reset()
        done = False
        while not done:
            env.render()
            actions = env.act(state)
            state, reward, done, info = env.step(actions)
        print('Episode {} finished'.format(i_episode))
    env.close()


if __name__ == '__main__':
    main()
```
### Docker Agent
The above example can be extended to use **DockerAgent** instead of a **RandomAgent**. The code below wraps a **SimpleAgent** inside Docker.  
```python
#!/usr/bin/python
"""Implementation of a simple deterministic agent using Docker."""

from pommerman import agents
from pommerman.runner import DockerAgentRunner


class MyAgent(DockerAgentRunner):
    """An example Docker agent class"""

    def __init__(self):
        self._agent = agents.SimpleAgent()

    def act(self, observation, action_space):
        return self._agent.act(observation, action_space)


def main():
    """Inits and runs a Docker Agent"""
    agent = MyAgent()
    agent.run()


if __name__ == "__main__":
    main()
```
* We will build a docker image with the name `pommerman/simple-agent` using the `Dockerfile` provided.
```shell
$ cd ~/playground
$ docker build -t pommerman/simple-agent -f examples/docker-agent/Dockerfile .
```

* The agent list seen in the previous example can now be updated. Note that a `port` argument (of an unoccupied port) is
needed to expose the HTTP server.
```python
#!/usr/bin/python
agent_list = [
    agents.SimpleAgent(),
    agents.RandomAgent(),
    agents.SimpleAgent(),
    agents.DockerAgent("pommerman/simple-agent", port=12345)
]
```
## Playing an interactive game
You can also play the game! See below for an example where one **PlayerAgent** controls with the `Arrow` keys and the other with the `WASD` keys.
```python
#!/usr/bin/python
agent_list = [
    agents.SimpleAgent(),
    agents.PlayerAgent(agent_control="arrows"), # Arrows = Move, Space = Bomb
    agents.SimpleAgent(),
    agents.PlayerAgent(agent_control="wasd"), # W,A,S,D = Move, E = Bomb
]
```

## NeurIPS 2018 Docker Agents

To test your agent against 2018 NeurIPS competition agents you can download an agent using `docker pull`...

```
docker pull multiagentlearning/hakozakijunctions
```

The following agents are available: `multiagentlearning/hakozakijunctions`, `multiagentlearning/dypm.1`, `multiagentlearning/dypm.2`, `multiagentlearning/navocado`, `multiagentlearning/skynet955`, `multiagentlearning/eisenach`

To use an agent once you have pulled it from docker hub use a command like the following.

```
pom_battle --agents=MyAgent,docker::multiagentlearning/navocado,player::arrows,docker::multiagentlearning/eisenach --config=PommeRadioCompetition-v2
```

## Useful information
1. Two agents cannot move to the same cell. They will bounce back to their prior places if they try. The same applies to bombs. If an agent and a bomb both try to move to the same space, then the agent will succeed but the bomb will bounce back.
2. If an agent with the can_kick ability moves to a cell with a bomb, then the bomb is kicked in the direction from which the agent came. The ensuing motion will persist until the bomb hits a wall, another agent, or the edge of the grid. 
3. When a bomb explodes, it immediately reaches its full blast radius. If there is an agent or a wall in the way, then it prematurely ends and destroys that agent or wall. 
4. If a bomb is in the vicinity of an explosion, then it will also go off. In this way, bombs can chain together.
5. The SimpleAgent is very useful as a barometer for your own efforts. Four SimpleAgents playing against each other have a win rate of ~18% each with the remaining ~28% of the time being a tie. Keep in mind that it **can** destroy itself. That can skew your own results if not properly understood.
