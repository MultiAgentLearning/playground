import requests
import pickle
import time

class _Agent(object):
    def __init__(self, agent):
        self._agent = agent

    def __getattr__(self, attr):
        return getattr(self._agent, attr)

    def act(self, obs):
        raise NotImplemented

    @staticmethod
    def has_key_input():
        return False

    def stop(self):
        pass


class PlayerAgent(_Agent):
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


class RandomAgent(_Agent):
    def act(self, obs, action_space):
        return action_space.sample()


class DockerAgent(_Agent):
    """TODO"""
    def __init__(self, agent, docker_image, docker_client, port, **kwargs):
        self._agent = agent
        self._docker_image = docker_image
        self._docker_client = docker_client
        self._port = port
        self._container = self._docker_client.containers.run(
            docker_image, detach=True, auto_remove=True, ports={80: port}, **kwargs)
        # TODO: Should really wait until http endpoint available instead of sleeping
        time.sleep(5)

    def act(self, obs, action_space):
        obs_serialized = pickle.dumps(obs, protocol=0).decode("utf-8")
        request_url = "http://localhost:{}/action".format(self._port)
        req = requests.post(request_url, json={"obs": obs_serialized})
        res = req.json()
        print(res)
        return res["action"]

    def stop(self):
        print("Stopping container..")
        if self._container:
            return self._container.remove(force=True)
