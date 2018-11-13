'''This is the basic docker agent runner'''
import abc
import logging
import json
from .. import constants
import numpy as np
from flask import Flask, jsonify, request

LOGGER = logging.getLogger(__name__)


class DockerAgentRunner(metaclass=abc.ABCMeta):
    """Abstract base class to implement Docker-based agent"""

    def __init__(self):
        pass

    @abc.abstractmethod
    def act(self, observation, action_space):
        """Given an observation, returns the action the agent should"""
        raise NotImplementedError()

    def run(self, host="0.0.0.0", port=10080):
        """Runs the agent by creating a webserver that handles action requests."""
        app = Flask(self.__class__.__name__)

        @app.route("/action", methods=["POST"])
        def action(): #pylint: disable=W0612
            '''handles an action over http'''
            data = request.get_json()
            observation = data.get("obs")
            observation = json.loads(observation)

            observation['teammate'] = constants.Item(observation['teammate'])
            for enemy_id in range(len(observation['enemies'])):
                observation['enemies'][enemy_id] = constants.Item(observation['enemies'][enemy_id])
            observation['position'] = tuple(observation['position'])
            observation['board'] = np.array(observation['board'], dtype=np.uint8)
            observation['bomb_life'] = np.array(observation['bomb_life'], dtype=np.float64)
            observation['bomb_blast_strength'] = np.array(observation['bomb_blast_strength'], dtype=np.float64)

            action_space = data.get("action_space")
            action_space = json.loads(action_space)
            action = self.act(observation, action_space)
            return jsonify({"action": action})

        @app.route("/init_agent", methods=["POST"])
        def init_agent(): #pylint: disable=W0612
            '''initiates agent over http'''
            data = request.get_json()
            id = data.get("id")
            id = json.loads(id)
            game_type = data.get("game_type")
            game_type = constants.GameType(json.loads(game_type))
            self.init_agent(id, game_type)
            return jsonify(success=True)

        @app.route("/shutdown", methods=["POST"])
        def shutdown(): #pylint: disable=W0612
            '''Requests destruction of any created objects'''
            self.shutdown()
            return jsonify(success=True)

        @app.route("/episode_end", methods=["POST"])
        def episode_end(): #pylint: disable=W0612
            '''Info about end of a game'''
            data = request.get_json()
            reward = data.get("reward")
            reward = json.loads(reward)
            self.episode_end(reward)
            return jsonify(success=True)

        @app.route("/ping", methods=["GET"])
        def ping(): #pylint: disable=W0612
            '''Basic agent health check'''
            return jsonify(success=True)

        LOGGER.info("Starting agent server on port %d", port)
        app.run(host=host, port=port)
