# Getting Started

# Pre-requisites

* [Python 3.6.0](https://www.python.org/downloads/release/python-360/)+ (including `pip`)
* [Docker](https://www.docker.com/) (only needed for `DockerAgent`)
* [virtualenv](https://virtualenv.pypa.io/en/stable/) (optional, for isolated Python environment)

# Installation

* **OPTIONAL**: Setup an isolated virtual Python environment by running the following commands
```
$ virtualenv </path/to/venv>
```
This environment needs to be activated for usage. Any package installations will now persist
in this virtual environment folder only.
```
source venv/bin/activate
```

* Clone the repository
```
$ git clone https://github.com/MultiAgentLearning/playground </path/to/playground>
```

* Install the `pommerman` package. This needs to be done every time the code is updated to get the
latest modules
```
$ cd </path/to/playground>
$ pip install -U .
```

# Examples

**NOTE**: There can only be **four** agents in the game.

## A Simple Example

A simple game run in a Free-For-All configuration can be found in [simple_ffa_run.py](../examples/simple_ffa_run.py) which
places two [SimpleAgent](../pommerman/agents/simple_agent.py)s and two [RandomAgent](../pommerman/agents/random_agent.py)s
on the board.

## Using A Docker Agent

As an extension to the above example, let us now replace one of the `RandomAgent`s with a
[DockerAgent](../pommerman/agents/docker_agent.py). For the sake of this example, a `DockerAgent` has
been provided which simply wraps the `SimpleAgent` seen above. All the necessary code is available
[here](../examples/docker-agent).

* We will build a docker image with the name "pommerman/simple-agent" using the `Dockerfile` provided.
```
$ cd </path/to/playground>
$ docker build -t pommerman/simple-agent -f examples/docker-agent/Dockerfile .
```

* The agent list seen in the previous example can now be updated. Note that the `port` argument is needed
to expose the HTTP server. Make sure this port is not occupied before running the example or use any different
port number.
```python
agent_list = [
    agents.SimpleAgent(),
    agents.RandomAgent(),
    agents.SimpleAgent(),
    agents.DockerAgent("pommerman/simple-agent", port=12345)
]
```

## Playing an interactive game

One can also become a player in the game by using [PlayerAgent](../pommerman/agents/player_agent.py). Let us
replace both `RandomAgent`s in the simple example by two human players.

```python
agent_list = [
    agents.SimpleAgent(),
    agents.PlayerAgent(agent_control="arrows"), # arrows to move, space to lay bomb
    agents.SimpleAgent(),
    agents.PlayerAgent(agent_control="wasd"), # W,A,S,D to move, E to lay bomb
]
```
