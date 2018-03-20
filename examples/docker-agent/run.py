"""Generic runner for docker agents"""

import os
import importlib

from pommerman.runner import DockerAgentRunner


def create_instance_from_path(path):
    """Creates an instance of an agent from an absolute path, like myagent.Agent"""
    module_name, class_name = path.rsplit(".", 1)
    class_ = getattr(importlib.import_module(module_name), class_name)
    assert issubclass(class_, DockerAgentRunner), "Agent must subclass DockerAgentRunner"
    return class_()


def main():
    agent_class_path = os.environ.get("AGENT_CLASS", "agent.Agent")
    agent = create_instance_from_path(agent_class_path)
    agent.run()


if __name__ == "__main__":
    main()
