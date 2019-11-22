'''An agent that preforms a random action each step'''
from . import BaseAgent
from pommerman.constants import Action
from pommerman.agents import filter_action
import random

class RandomAgent(BaseAgent):
    """The Random Agent that returns random actions given an action_space."""

    def act(self, obs, action_space):
        return action_space.sample()

class RandomAgentNoBomb(BaseAgent):
    """The Random Agent that returns random actions given an action_space but never sets bombs."""

    def act(self, obs, action_space):
        action = action_space.sample()
        if Action.Bomb.value == action:
            action = Action.Stop.value
        return action

class SlowRandomAgentNoBomb(BaseAgent):
    """The Random Agent that returns random actions given an action_space, but never places bombs and often just sits."""
    def __init__(self):
        self.act_count = 0
        super(SlowRandomAgentNoBomb, self).__init__()

    def act(self, obs, action_space):
        action = action_space.sample()
        self.act_count += 1
        if Action.Bomb.value == action or self.act_count % 4 != 3:
            action = Action.Stop.value
        return action

class TimedRandomAgentNoBomb(BaseAgent):
    """Random Agent that returns random actions given an action_space, but never places bombs and stops doing anything after a number of moves."""
    def __init__(self):
        self.act_count = 0
        super(TimedRandomAgentNoBomb, self).__init__()

    def act(self, obs, action_space):
        MAX_MOVES = 30
        action = Action.Stop.value
        if self.act_count < MAX_MOVES:
            possible_action = action_space.sample()
            if Action.Bomb.value != possible_action:
                self.act_count += 1
                action = possible_action
        return action


class StaticAgent(BaseAgent):
    """ Static agent"""

    def act(self, obs, action_space):
        return Action.Stop.value

class SmartRandomAgent(BaseAgent):
    """ random with filtered actions"""
    def act(self, obs, action_space):
        valid_actions=filter_action.get_filtered_actions(obs)
        if len(valid_actions) ==0:
            valid_actions.append(Action.Stop.value)
        return random.choice(valid_actions)

class SmartRandomAgentNoBomb(BaseAgent):
    """ random with filtered actions but no bomb"""
    def act(self, obs, action_space):
        valid_actions=filter_action.get_filtered_actions(obs)
        if Action.Bomb.value in valid_actions:
            valid_actions.remove(Action.Bomb.value)
        if len(valid_actions) ==0:
            valid_actions.append(Action.Stop.value)
        return random.choice(valid_actions)
