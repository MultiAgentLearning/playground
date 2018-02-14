# Playground

#### First time? check out our [website](www.pommerman.com) for more information and our [Discord](https://discordapp.com/invite/wjVJEDc) to join the community.

Playground hosts Pommerman, a clone of Bomberman built for AI research. People from around the world submit agents that they've trained to play. We run regular competitions on our servers and report the results and replays.

There are three variants for which you can enter your agents to compete:

* FFA: Free For All where four agents enter and one leaves. It tests planning, tactics, and cunning.
* Team: 2v2 where two teams of agents enter and one team wins. It tests cooperation, planning, and tactics.
* Team Radio: Like Team but each agent has a radio that they can use to convey 2 words each step from a dictionary of size 8.

#### Why should I participate?

* You are a machine learning researcher and similarly recognize the lack of approachable benchmarks for this subfield. Help us rectify this and prove that your algorithm is better than others.
* You want to contribute to multi agent or communication research. This is first and foremost a platform for doing research and everything that we do here will eventually get published with generous (or primary) support from us.
* You really like(d) Bomberman and are fascinated by AI. This is a great opportunity to learn how to build intelligent agents.
* You want the glory of winning an AI competition. We are going to publicize the results widely.
* You think AI is dumb and can make a deterministic system that beats any learned agent.

#### How do I train agents?

Most open-source research tools in this domain have been designed with single agents in mind. We will be developing resources towards standardizing multi-agent learning. In the meantime, we have provided an example training script in train_with_tensorforce.py. It demonstrates how to wrap the Pommerman environments such that they can be trained with popular libraries like TensorForce.

#### How do I submit agents that I have trained?

The setup for submitting agents will be live shortly. It involves making a [Docker](https://docs.docker.com/get-started/) container that runs your agent. We then read and upload your docker file via Github OAuth. You retain the ownership and license of the agents. We will not look at or use your code; we are just going to run your agent in competitions on our servers. We have an example agent that already works and further instructions are in the games/a/docker directory.

#### Who is running this?

[Cinjon Resnick](http://twitter.com/cinjoncin), [Denny Britz](https://twitter.com/dennybritz), and [David Ha](https://twitter.com/hardmaru) are the folks behind this. We are generously supported by a host of other people, including [Kyunghyun Cho](https://twitter.com/kchonyc), [Joan Bruna](https://twitter.com/joanbruna) and [Jason Weston](https://research.fb.com/people/weston-jason/). You can find us in the [Discord](https://discordapp.com/invite/wjVJEDc).

#### How can I help?

While in general we are open to all kinds of improvements, here's a list that we see as priorities from the community:

1. Better graphics: We want Pommerman to have a more welcoming feel. Right now, it's just pixels. Even replacing the squares with sprites would be really nice.
2. Better (and more) baselines: We released the SimpleAgent as a first baseline to beat before submitting agents to compete. We would like to see more there, each with a degree of difficulty and geared towards the different competitions.
3. Make tutorials: We plan to make a tutorial for each of the learned Agents that we enter. However, it would be awesome if others did as well. This extends from well-documented algorithms like DQN all the way to less considered ones like Evolutionary Learning.
