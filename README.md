# Deep Learning Pommerman Project

For this project, we are attempting to create our own reinforcement learning agents that will be able to apply teamwork in a novel way.

## Agent Design

Much of the code is based on the Skynet955 agent that placed 5th in NeurIPS in 2018.
https://hub.docker.com/r/multiagentlearning/skynet955

https://www.borealisai.com/en/blog/pommerman-team-competition-or-how-we-learned-stop-worrying-and-love-battle/

https://github.com/BorealisAI/pommerman-baseline

## Getting started

### Installation

1. Install CUDA and Nvidia Drivers (if you have an NVIDIA GPU)
1. Clone the repo
1. Create a virtual or conda environment
1. Source your environment. this will vary depending on your environment; for virtualenv in linux: 

   ```bash 
   source venv/bin/activate 
   ```
   
1. Install dependencies

   ```bash
   pip3 install -r requirements.txt
   pip3 install -r requirements_extra.txt
   ```
   
1. Install code (must be done everytime pommerman libraries are changed):
   
   ```bash
   python3 setup.py build
   python3 setup.py install
   python3 setup.py install_lib
   ```

1. Test it: 

   ```bash 
   python3 examples/simple_ffa_run.py 
   ```

### Training

If you want to train the skynet model, follow these directions

1. Modify params file for your setup (be sure to set start_iteration to 0 if starting with an untrained network).
1. Add CUDA devices to your environment variables if you have any (comma separated):

   ```bash
   echo export CUDA_VISIBLE_DEVICES=0 >> ~/.bashrc
   ```
1. If you do not have CUDA, remove the --device_id argument from train.sh script.
1. Run training with set params: 
   
   ```bash 
   source train.sh params log.txt 
   ```
   
1. Training will run for a while and be stored in nn_model_dir
1. Modify  examples/simple_team_run_CNNskynet.py to view your trained agent as of last stored checkpoint and then test it: 

   ```bash 
   python3 examples/simple_team_run_CNNskynet.py 
   ```


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
