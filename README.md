# Deep Learning Pommerman Project

For this project, we are attempting to create our own reinforcement learning agents that will be able to apply teamwork in a novel way.

## Agent Design

Much of code is pulled from the Skynet955 agent that placed 5th in NeurIPS in 2018.
https://hub.docker.com/r/multiagentlearning/skynet955
https://www.borealisai.com/en/blog/pommerman-team-competition-or-how-we-learned-stop-worrying-and-love-battle/
https://github.com/BorealisAI/pommerman-baseline

## Getting started

### Installation

1. Create a virtual or conda environment
2. Source your environment
3. pip3 install -r requirements.txt
4. pip3 install -r requirements_extra.txt
5. Install everything:
6. python3 setup.py build
7. python3 setup.py install
8. python3 setup.py install_lib
9. Test it
10. python3 examples/simple_ffa_run.py

### Training

If you want to train the skynet model, follow these directions

1. Modify params file for your setup.
2. If you do not have CUDA, remove the --device_id argument from train.sh script.
3. source train.sh params log.txt
4. Training will run for a while and be stored in nn_model_dir
5. Modify  examples/simple_team_run_CNNskynet.py to view your trained agent as of last stored checkpoint
6. python3 examples/simple_team_run_CNNskynet.py


## Playground Info

> First time? check out our [website](https://www.pommerman.com) for more information,
> our [Discord](https://discordapp.com/invite/wjVJEDc) to join the community,
> or read the [documentation](./docs) to get started.

Playground hosts Pommerman, a clone of Bomberman built for AI research. People from around the world submit agents that they've trained to play. We run regular competitions on our servers and report the results and replays.

There are three variants for which you can enter your agents to compete:

* FFA: Free For All where four agents enter and one leaves. It tests planning, tactics, and cunning. The board is fully observable.
* Team (The NIPS '18 Competition environment): 2v2 where two teams of agents enter and one team wins. It tests planning, and tactics, and cooperation. The board is partially observable.
* Team Radio: Like team in that a it's a 2v2 game. Differences are that the agents each have a radio that they can use to convey 2 words from a dictionary of size 8 each step.

#### How do I train agents?

Most open-source research tools in this domain have been designed with single agents in mind. We will be developing resources towards standardizing multi-agent learning. In the meantime, we have provided an example training script in train_with_tensorforce.py. It demonstrates how to wrap the Pommerman environments such that they can be trained with popular libraries like TensorForce.

#### How do I submit agents that I have trained?

The setup for submitting agents will be live shortly. It involves making a [Docker](https://docs.docker.com/get-started/) container that runs your agent. We then read and upload your docker file via Github Deploy Keys. You retain the ownership and license of the agents. We will only look at your code to ensure that it is safe to run, doesn't execute anything malicious, and does not cheat. We are just going to run your agent in competitions on our servers. We have an example agent that already works and further instructions are in the games/a/docker directory.


#### Original codebase

Find the orignal codebase we forked from [here](https://github.com/MultiAgentLearning/playground/).

# Citation
Since we are using Pommerman environment in our research, we cite it using this [bibtex file](../master/docs/pommerman.bib) in docs.
