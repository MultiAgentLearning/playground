# Playground

> First time? check out our [website](https://www.pommerman.com) for more information,
> our [Discord](https://discordapp.com/invite/wjVJEDc) to join the community,
> or read the [documentation](./docs) to get started.

Playground hosts Pommerman, a clone of Bomberman built for AI research. People from around the world submit agents that they've trained to play. We run regular competitions on our servers and report the results and replays.

There are three variants for which you can enter your agents to compete:

* FFA: Free For All where four agents enter and one leaves. It tests planning, tactics, and cunning. The board is fully observable.
* Team (The NIPS '18 Competition environment): 2v2 where two teams of agents enter and one team wins. It tests planning, and tactics, and cooperation. The board is partially observable.
* Team Radio: Like team in that a it's a 2v2 game. Differences are that the agents each have a radio that they can use to convey 2 words from a dictionary of size 8 each step.

#### Why should I participate?

* You are a machine learning researcher and similarly recognize the lack of approachable benchmarks for this subfield. Help us rectify this and prove that your algorithm is better than others.
* You want to contribute to multi agent or communication research. This is first and foremost a platform for doing research and everything that we do here will eventually get published with generous (or primary) support from us.
* You really like(d) Bomberman and are fascinated by AI. This is a great opportunity to learn how to build intelligent agents.
* You want the glory of winning an AI competition. We are going to publicize the results widely.
* You think AI is dumb and can make a deterministic system that beats any learned agent.

#### How do I train agents?

Most open-source research tools in this domain have been designed with single agents in mind. We will be developing resources towards standardizing multi-agent learning. In the meantime, we have provided an example training script in train_with_tensorforce.py. It demonstrates how to wrap the Pommerman environments such that they can be trained with popular libraries like TensorForce.

#### How do I submit agents that I have trained?

The setup for submitting agents will be live shortly. It involves making a [Docker](https://docs.docker.com/get-started/) container that runs your agent. We then read and upload your docker file via Github Deploy Keys. You retain the ownership and license of the agents. We will only look at your code to ensure that it is safe to run, doesn't execute anything malicious, and does not cheat. We are just going to run your agent in competitions on our servers. We have an example agent that already works and further instructions are in the games/a/docker directory.

#### Who is running this?

[Cinjon Resnick](http://twitter.com/cinjoncin), [Denny Britz](https://twitter.com/dennybritz), [David Ha](https://twitter.com/hardmaru), [Jakob Foerster](https://www.linkedin.com/in/jakobfoerster/), and [Wes Eldridge](https://twitter.com/weseldridge) are the folks behind this. We are generously supported by a host of other people, including [Kyunghyun Cho](https://twitter.com/kchonyc), [Joan Bruna](https://twitter.com/joanbruna), [Julian Togelius](http://julian.togelius.com/) and [Jason Weston](https://research.fb.com/people/weston-jason/). You can find us in the [Discord](https://discordapp.com/invite/wjVJEDc).

Pommerman is immensely appreciate of the generous assistance it has received from Jane Street Capital, NVidia, Facebook AI Research, and Google Cloud.

#### How can I help?

To see the ways you can get invovled with the project head over to our [Contributing Guide](https://github.com/MultiAgentLearning/playground/blob/master/CONTRIBUTING.md) and checkout our current [issues](https://github.com/MultiAgentLearning/playground/issues).

# Contributing

We welcome contributions through pull request. See [CONTRIBUTING](../master/CONTRIBUTING.md) for more details.

# Code of Conduct

We strive for an open community. Please read over our [CODE OF CONDUCT](../master/CODE_OF_CONDUCT.md)
