from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from collections import defaultdict
import json
import math
import os

# TODO: Do this with relative imports and folder __init__ instead.
import sys
sys.path.insert(0, os.path.join(sys.path[0], '..'))

import gym
from gym.utils import seeding
import logging
import numpy as np
import requests

import Box2D
from Box2D.b2 import (edgeShape, fixtureDef, polygonShape)

import agent
import board
import gym_multi_agent
import utility

FPS = 20


class Hockey(gym.Env):
    """Environment for playing hockey.

    Args:
      num_agents_per_team: The integer number of players on a team.
      num_gas_bins: Number of discrete outputs for the gas bins. Will be normalized to [0, 1].
      num_brake_bins: Number of discrete outputs for the brake bins. Will be normalized to [0, 1].
      num_steering_bins: Number of discrete outputs for the steering. Will be normalized to [-pi/4, pi/4]
        and applied relative to the current angle.
      lidar_angles: The degree angles that the lidar point with 0deg being the car front.
      max_steps: The maximum number of steps to take in a round (episode).
    """
    metadata = {
        'render.modes': ['human', 'rgb_array'],
        'video.frames_per_second': FPS
    }

    def __init__(self, num_agents_per_team=None, num_gas_bins=10, num_brake_bins=10, num_steer_bins=10, lidar_angles=None,
                 max_steps=1000, *args, **kwargs):
        lidar_angles = lidar_angles or list(range(-45, 45, 5))

        # We make these as lambdas because it's easier to remake them every time the game resets than it is
        # to properly clear everything away back to the game start position.
        self._make_world = lambda: Box2D.b2World((0, 0), contactListener=board.GoalListener(self))
        self._make_board = lambda world: board.make_game(world)
        self._make_players = lambda world: agent.make_agents(
            world, num_agents_per_team=num_agents_per_team,
            gas_bins=[0, num_gas_bins-1], brake_bins=[0, num_brake_bins-1], steer_bins=[0, num_steer_bins-1]
        )

        self._max_steps = max_steps
        self.action_space = gym_multi_agent.MultiDiscrete(
            [[0, num_gas_bins-1], [0, num_brake_bins-1], [0, num_steer_bins-1]],
            num_agents_per_team * 2)
        self.observation_space = self._get_observation_space(lidar_angles, num_agents_per_team)
        self.seed(kwargs.get("seed"))

    def _seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        np.random.seed(seed % (2**32 - 1))
        return [seed]

    def _get_observation_space(self, lidar_angles, num_agents_per_team):
        """Per-agent lidar and personal observations. Later versions of this will add messages."""
        min_obs = []
        max_obs = []

        # Lidar Observations: collision distances and types.
        min_obs.extend([0 for _ in lidar_angles])
        min_obs.extend([0 for _ in utility.CATEGORY_BITS])
        max_obs.extend([300 for _ in lidar_angles])
        max_obs.extend([len(utility.CATEGORY_BITS) for _ in utility.CATEGORY_BITS])

        # Personal observations: team, x, y, vx, vy, wheel_angle, hull_angle, time_remaining, *score]
        # TODO: Check that these bounds are sufficient.
        min_obs.extend([1, -100, -43, -50, -50, 0, 0, 0, 0, 0])
        max_obs.extend([2, 100, 43, 50, 50, 2*np.pi, 2*np.pi, self._max_steps, 25, 25])

        min_obs = np.array(min_obs, dtype=np.float32)
        max_obs = np.array(max_obs, dtype=np.float32)
        return gym.spaces.Box(
            np.stack(num_agents_per_team * 2 * [min_obs]),
            np.stack(num_agents_per_team * 2 * [max_obs])
        )

    def _step(self, actions):
        """Take a step in the environment.

        Args:
          actions: Actions are an array of (steer, gas, brake) per agent, where the agents
            are ordered s.t. team 1 is before team 2.

        Returns:
          state: The array of observations per car.
          rewards: Array of scalar reward per car.
          dones: Array of whether each car has completed (crashed or reached exit).
          info: Empty dict.
        """
        self._scored = False

        self._apply_actions(actions)
        for player in self._players:
            player.step(1.0 / FPS)

        self._world.Step(1.0 / FPS, 6 * 30, 2 * 30)
        self._timestep += 1.0 / FPS
        self._stepcount += 1.0

        observations = self.get_observations()
        self._done = done = (self._stepcount == self._max_steps)
        rewards = [0.0 for _ in self._players]
        if self._score_on_goal is not None:
            rewards = [float(player.team != self.env._score_on_goal) for player in self._players]
            self._score[2 - self.env._score_on_goal] += 1
            self._scored = True
            self._score_on_goal = None

        return observations, rewards, done, {}

    def _apply_actions(self, actions):
        for player, action in zip(self._players, actions):
            player.steer(-action[0])
            player.gas(action[1])
            player.brake(action[2])

    def get_observations(self):
        """Get the observations from the players.

        Returns:
          observations: The array of each player's observations.
        """
        observations = []
        for player in self._players:
            player.set_lidar_observations(self._world)
            player.set_personal_observations(self._world, self._score, self._max_steps - self._stepcount)
            observations.append(player.lidar_observations + player.personal_observations)
        return observations

    def _reset(self):
        self._world = self._make_world() # a Box2D.b2World object
        self._board  = self._make_board(self._world)
        self._players = self._make_players(self._world)
        self._stepcount = 0.0
        self._timestep = 0.0
        self._score = [0, 0]
        self._score_on_goal = None
        self._scored = False
        self._done = False
        return self.get_observations()

    def _render(self, mode='human', close=False):
        print("RENDERING !")
        if close:
            try:
                r = requests.post(
                    'http://localhost:5000/write', json={"close": True})
            except:
                pass
            return

        r = requests.post(
            'http://localhost:5000/write',
            json={
                "close": False,
                "board": self.render_board(), 
                "players": self.render_players(),
                "timestep": "%.3f" % self._timestep,
                "stepcount": self._stepcount,
                "score": self._score,
                "scored": self._scored,
                "done": self._done
            }
        )

    def render_board(self):
        return self._board.render()

    def render_players(self):
        return [player.render() for player in self._players]
