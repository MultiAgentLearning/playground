'''The HTTP agent - provides observation using http push to remote
   agent and expects action in the reply'''
import json
import time
import os
import threading
import requests

from . import BaseAgent
from .. import utility
from .. import characters


class HttpAgent(BaseAgent):
    """The HTTP Agent that connects to a port with a remote agent where the
       character runs. It uses the same interface as the docker agent and
       is useful for debugging."""

    def __init__(self,
                 port=8080,
                 host='localhost',
                 timeout=120,
                 character=characters.Bomber):
        self._port = port
        self._host = host
        self._timeout = timeout
        super(HttpAgent, self).__init__(character)
        self._wait_for_remote()

    def _wait_for_remote(self):
        """Wait for network service to appear. A timeout of 0 waits forever."""
        timeout = self._timeout
        backoff = .25
        max_backoff = min(timeout, 16)

        if timeout:
            # time module is needed to calc timeout shared between two exceptions
            end = time.time() + timeout

        while True:
            try:
                now = time.time()
                if timeout and end < now:
                    print("Timed out - %s:%s" % (self._host, self._port))
                    raise

                request_url = 'http://%s:%s/ping' % (self._host, self._port)
                req = requests.get(request_url)
                self._acknowledged = True
                return True
            except requests.exceptions.ConnectionError as e:
                print("ConnectionError: ", e)
                backoff = min(max_backoff, backoff * 2)
                time.sleep(backoff)
            except requests.exceptions.HTTPError as e:
                print("HTTPError: ", e)
                backoff = min(max_backoff, backoff * 2)
                time.sleep(backoff)

    def init_agent(self, id, game_type):
        super(HttpAgent, self).init_agent(id, game_type)
        request_url = "http://{}:{}/init_agent".format(self._host, self._port)
        try:
            req = requests.post(
                request_url,
                timeout=0.5,
                json={
                    "id": json.dumps(id, cls=utility.PommermanJSONEncoder),
                    "game_type": json.dumps(game_type, cls=utility.PommermanJSONEncoder)
                })
        except requests.exceptions.Timeout as e:
            print('Timeout in init_agent()!')

    def act(self, obs, action_space):
        obs_serialized = json.dumps(obs, cls=utility.PommermanJSONEncoder)
        request_url = "http://{}:{}/action".format(self._host, self._port)
        try:
            req = requests.post(
                request_url,
                timeout=0.15,
                json={
                    "obs":
                    obs_serialized,
                    "action_space":
                    json.dumps(action_space, cls=utility.PommermanJSONEncoder)
                })
            action = req.json()['action']
        except requests.exceptions.Timeout as e:
            print('Timeout!')
            # TODO: Fix this. It's ugly.
            num_actions = len(action_space.shape)
            if num_actions > 1:
                return [0] * num_actions
            else:
                return 0
        return action

    def episode_end(self, reward):
        request_url = "http://{}:{}/episode_end".format(self._host, self._port)
        try:
            req = requests.post(
                request_url,
                timeout=0.5,
                json={
                    "reward": json.dumps(reward, cls=utility.PommermanJSONEncoder)
                })
        except requests.exceptions.Timeout as e:
            print('Timeout in episode_end()!')

    def shutdown(self):
        request_url = "http://{}:{}/shutdown".format(self._host, self._port)
        try:
            req = requests.post(
                request_url,
                timeout=0.5,
                json={ })
        except requests.exceptions.Timeout as e:
            print('Timeout in shutdown()!')
