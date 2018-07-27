# Contributor Guide

We are excited to have your help building Pommerman. There are many ways to contribute to Pommerman. You can contribute code, write documentation and tutorials, or answer questions in our Discord community. Below is a general overview of contributing. We really look forward to your help!

## Code of Conduct

We strive to foster an open community. Please read our [Code of Conduct](https://github.com/MultiAgentLearning/playground/blob/master/CODE_OF_CONDUCT.md).

## How to contribute

Below is a list of different ways for you to contribute.

* Bugfixes
* New features
* Documentation
* Design
* Tutorials

This list isn't complete. We very much welcome other ideas. Please come talk to us in our [Discord](https://discord.gg/wjVJEDc) chat.

Here's a list that we see as priorities from the community:

1. Better graphics: We want Pommerman to have a more welcoming feel. Right now, it's just pixels. Even replacing the squares with sprites would be really nice. [Issue 5](https://github.com/MultiAgentLearning/playground/issues/7)
2. Better (and more) baselines: We released the SimpleAgent as a first baseline to beat before submitting agents to compete. We would like to see more there, each with a degree of difficulty and geared towards the different competitions.
3. Make tutorials: We plan to make a tutorial for each of the learned Agents that we enter. However, it would be awesome if others did as well. This extends from well-documented algorithms like DQN all the way to less considered ones like Evolutionary Learning.


## Contributing Code

The general workflow for commiting code.

* Fork the repository
* Create a local branch for your fix
* Commit your changes and push your created branch to your fork
* Open a new pull request into our master branch

## Formating

**Spacing** - In between methods in classes use one line space. Functions, Classes, and groups of variables outside of a Class use two line spaces.

**Naming** - Classes use caps camelcase whereas functions, methods, and variables use snake case. Constants are all caps and use snake case. Names should not exceed 80 characters.

**Commenting** - Doc string are required for all files, modules, classes, and functions. Comment complicated code or code that isn't easily understood.

 
## Linting 

This project uses pylint to ensure code is formatted correctly. You can lint a module space or a single file by using one of the following terminal commands.

```
# A directory or module
pylint pommerman/

# A single file
pylint pommerman/utility.
```

If your code doesn't pass linting please make the updates to ensure your code passes. PR's will not be accepted if your code doesn't pass the linter. 

You can dig into the how we lint by taking a look at the `pylintrc` file in the root of this repo.

**Linting** - Please lint according to the google style. An easy way to do this is to use the yapf pip package: `yapf --style google <path/to/file>`. Include the flag `-i` to edit the file in place.

**Linting** - Please lint according to the google style. An easy way to do this is to use the yapf pip package: `yapf --style google <path/to/file>`. Include the flag `-i` to edit the file in place.

## Discord

Discussions, correspondence, and announcements often happen in Discord. You can get access through our [Discord invite.](https://discord.gg/wjVJEDc)



