import requests
import pickle
import time
import threading
import os

class Agent(object):
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
    def __init__(self, agent, key_input, on_key_press, on_key_release):
        self._agent = agent
        self._key_input = key_input
        self.on_key_press = on_key_press
        self.on_key_release = on_key_release

    def act(self, obs, action_space, debug=False):
        return self._key_input['curr']

    @staticmethod
    def has_key_input():
        return True


class RandomAgent(Agent):
    def act(self, obs, action_space, debug=False):
        return action_space.sample()


class DockerAgent(Agent):
    """Connects to an agent running in a Docker container"""
    def __init__(self, agent, docker_image, docker_client, port, **kwargs):
        self._agent = agent
        self._docker_image = docker_image
        self._docker_client = docker_client
        self._port = port
        self._container = None
        container_thread = threading.Thread(target=self._run_container, daemon=True)
        container_thread.start()
        # TODO: Should really wait until http endpoint available instead of sleeping
        time.sleep(2)

    def _run_container(self):
        print("Starting container...")

        # Any environment variables that start with DOCKER_AGENT are passed to the container
        env_vars = {}
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

    def act(self, obs, action_space, debug=False):
        obs_serialized = pickle.dumps(obs, protocol=0).decode("utf-8")
        request_url = "http://localhost:{}/action".format(self._port)
        req = requests.post(request_url, json={
            "obs": obs_serialized,
            "action_space": pickle.dumps(action_space, protocol=0).decode("utf-8")
        })
        res = req.json()
        return res["action"]

    def shutdown(self):
        print("Stopping container..")
        if self._container:
            return self._container.remove(force=True)
