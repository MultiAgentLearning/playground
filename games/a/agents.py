"""The different Agent classes available as input to run_battle.py."""

import requests
import pickle
import time
import threading
import os


class Agent(object):
    """Parent abstract Agent."""

    def __init__(self, agent):
        self._agent = agent

    def __getattr__(self, attr):
        return getattr(self._agent, attr)

    def act(self, obs, action_space):
        raise NotImplemented

    @staticmethod
    def has_key_input():
        return False

    def shutdown(self):
        pass


class PlayerAgent(Agent):
    """The Player Agent that lets the user control a character."""
    def __init__(self, agent, key_input, on_key_press, on_key_release):
        self._agent = agent
        self._key_input = key_input
        self.on_key_press = on_key_press
        self.on_key_release = on_key_release

    def act(self, obs, action_space):
        return self._key_input['curr']

    @staticmethod
    def has_key_input():
        return True


class RandomAgent(Agent):
    """The Random Agent that returns random actions given an action_space."""
    def act(self, obs, action_space):
        return action_space.sample()


class DockerAgent(Agent):
    """The Docker Agent that Connects to a Docker container where the character runs."""
    def __init__(self, agent, docker_image, docker_client, server, port, env_vars=None, **kwargs):
        self._agent = agent
        self._docker_image = docker_image
        self._docker_client = docker_client
        self._server = server
        self._port = port
        self._container = None
        self._env_vars = env_vars or {}

        container_thread = threading.Thread(target=self._run_container, daemon=True)
        container_thread.start()
        self._wait_for_docker(self._server, self._port, 32)

    def _run_container(self):
        print("Starting container...")

        # Any environment variables that start with DOCKER_AGENT are passed to the container
        env_vars = self._env_vars
        for key, value in os.environ.items():
            if not key.startswith("DOCKER_AGENT_"):
                continue
            env_key = key.replace("DOCKER_AGENT_", "")
            env_vars[env_key] = value

        self._container = self._docker_client.containers.run(
            self._docker_image, detach=True, auto_remove=True,
            ports={10080: self._port}, environment=env_vars)
        for line in self._container.logs(stream=True):
            print(line.decode("utf-8").strip())

    @staticmethod
    def _wait_for_docker(server, port, timeout=None):
        """Wait for network service to appear.

        Args:
          port: Integer port.
          timeout: Seconds to wait. 0 waits forever.
        """
        backoff = .25
        max_backoff = min(timeout, 16)

        if timeout:
            # time module is needed to calc timeout shared between two exceptions
            end = time.time() + timeout

        while True:
            try:
                now = time.time()
                if timeout and end < now:
                    return False

                request_url = '%s:%s/ping' % (server, port) # 'http://localhost', 83
                req = requests.get(request_url)
                return True
            except requests.exceptions.ConnectionError as e:
                print("ConnectionError: ", e)
                backoff = min(max_backoff, backoff*2)
                time.sleep(backoff)
            except requests.exceptions.HTTPError as e:
                print("HTTPError: ", e)
                backoff = min(max_backoff, backoff*2)
                time.sleep(backoff)
            except docker.errors.APIError as e:
                print("This is a Docker error. Please fix: ", e)
                raise

    def act(self, obs, action_space):
        obs_serialized = pickle.dumps(obs, protocol=0).decode("utf-8")
        request_url = "http://localhost:{}/action".format(self._port)
        try:
            req = requests.post(request_url, timeout=0.25, json={
                "obs": obs_serialized,
                "action_space": pickle.dumps(action_space, protocol=0).decode("utf-8")
            })
            action = req.json()['action']
        except requests.exceptions.Timeout as e:
            print('Timeout!')
            # TODO: Fix this. It's ugly.
            action = [0]*len(action_space.shape)
            if len(action) == 1:
                action = action[0]
        return action

    def shutdown(self):
        print("Stopping container..")
        if self._container:
            return self._container.remove(force=True)


class TensorForceAgent(Agent):
    """The TensorForceAgent. Acts through the algorith, not here."""
    def __init__(self, agent, algorithm):
        self._agent = agent
        self.algorithm = algorithm

    def act(self, obs, action_space):
        pass

    def initialize(self, env):
        from gym import spaces
        from tensorforce.agents import PPOAgent

        if self.algorithm == "ppo":
            if type(env.action_space) == spaces.Tuple:
                actions_spec = {str(num): {'type': int, 'num_actions': space.n}
                                for num, space in enumerate(env.action_space.spaces)}
            else:
                actions_spec = dict(type='int', num_actions=env.action_space.n)

            return PPOAgent(
                states_spec=dict(type='float', shape=env.observation_space.shape),
                actions_spec=actions_spec,
                network_spec=[
                    dict(type='dense', size=64),
                    dict(type='dense', size=64)
                ],
                batch_size=128,
                step_optimizer=dict(
                    type='adam',
                    learning_rate=1e-4
                )
            )
        return None
