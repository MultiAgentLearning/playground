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
            action = [0] * len(action_space.shape)
            if len(action) == 1:
                action = action[0]
        return action
