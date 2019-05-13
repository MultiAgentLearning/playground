# Getting Started

# Pre-requisites

* [Python 3.6.0](https://www.python.org/downloads/release/python-360/)+ (including `pip`)
* [Docker](https://www.docker.com/) (only needed for `DockerAgent`)
* [virtualenv](https://virtualenv.pypa.io/en/stable/) (optional, for isolated Python environment)

# Installation

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

# Examples

## A Simple Example

The [simple_ffa_run.py](../examples/simple_ffa_run.py) runs a sample Free-For-All game with two
[SimpleAgent](../pommerman/agents/simple_agent.py)s and two [RandomAgent](../pommerman/agents/random_agent.py)s
on the board.

## Using A Docker Agent

The above example can be extended to use [DockerAgent](../pommerman/agents/docker_agent.py) instead of a
[RandomAgent](../pommerman/agents/random_agent.py). [examples/docker-agent](../examples/docker-agent) contains
the code to wrap a [SimpleAgent](../pommerman/agents/simple_agent.py) inside Docker.


* We will build a docker image with the name "pommerman/simple-agent" using the `Dockerfile` provided.
```
$ cd ~/playground
$ docker build -t pommerman/simple-agent -f examples/docker-agent/Dockerfile .
```

* The agent list seen in the previous example can now be updated. Note that a `port` argument (of an unoccupied port) is
needed to expose the HTTP server.
```python
agent_list = [
    agents.SimpleAgent(),
    agents.RandomAgent(),
    agents.SimpleAgent(),
    agents.DockerAgent("pommerman/simple-agent", port=12345)
]
```

## Playing an interactive game

You can also play the game! See below for an example where one [PlayerAgent](../pommerman/agents/player_agent.py)
controls with the `arrow` keys and the other with the `wasd` keys.


```python
agent_list = [
    agents.SimpleAgent(),
    agents.PlayerAgent(agent_control="arrows"), # arrows to move, space to lay bomb
    agents.SimpleAgent(),
    agents.PlayerAgent(agent_control="wasd"), # W,A,S,D to move, E to lay bomb
]
```

## Submitting an Agent.

In order to submit an agent, you need to create an account at 
[pommerman.com](https://pommerman.com). You can do this by registering with your 
email address or logging in with your Github account.

Once you have created an account, login and navigate to your profile - 
[Pommerman profile](https://pommerman.com/me). To submit an agent, fill in the 
form with your agent's name, an ssh git url, and the path to your agent's Docker 
file from the github repository's top level directory. Please make sure that 
your docker file builds properly beforehand.

Next, you will need to add an ssh deploy key to your account so we can access 
your agent's repo. This is provided to you along with instructions after 
registering the agent.

Before doing all of this, note that we use Docker to run the agents. The best example for making a Docker agent is in the repo in the examples/docker-agent directory. This *must* work in order to properly enter an agent, and we suggest using the accompanying pom_battle cli command (or equivalently run_battle.py) to test out your Docker implementation. If you are having trouble still, feel free to ask questions on our Discord channel.

## NIPS Competition Information:

Each competitor will submit two agents that will be teamed together. These agents can be the same one and can be in the same repository even, but we expect there to be two submissions for each entrant. We additionally expect there to be notable differences among the submissions. Similarly to the June 3rd competition, we will examine the code before running it on our servers and collusion will not be tolerated.

The competition will be held live at NIPS 2018 in Montreal. We would prefer it if serious entrants were there, but that is not a requirement.

## Actually Getting Started

Here is some information that may help you more quickly develop successful agents:

1. Two agents cannot move to the same cell. They will bounce back to their prior places if they try. The same applies to bombs. If an agent and a bomb both try to move to the same space, then the agent will succeed but the bomb will bounce back.
2. If an agent with the can_kick ability moves to a cell with a bomb, then the bomb is kicked in the direction from which the agent came. The ensuing motion will persist until the bomb hits a wall, another agent, or the edge of the grid. 
3. When a bomb explodes, it immediately reaches its full blast radius. If there is an agent or a wall in the way, then it prematurely ends and destroys that agent or wall. 
4. If a bomb is in the vicinity of an explosion, then it will also go off. In this way, bombs can chain together.
5. The SimpleAgent is very useful as a barometer for your own efforts. Four SimpleAgents playing against each other have a win rate of ~18% each with the remaining ~28% of the time being a tie. Keep in mind that it _can_ destroy itself. That can skew your own results if not properly understood.
