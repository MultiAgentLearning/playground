### Run a Docker agent

This is a sample Docker directory. There is an agent in the pommerman subdirectory that plays just like the
SimpleAgent in `pommerman/agents/simple_agent.py`. In order to use this in a Docker setup, you should:

1. Build the test agent by running the following bash command from the project root. This command will build a Docker container made up primarily of the pip packages in requirements.txt.

```bash
docker build -t pommerman/test-agent -f examples/docker-agent/Dockerfile .
```

2. Run the docker agent by starting a battle as in the following command from the top level directory. It will start a battle among the docker agent and three SimpleAgents, where the former is Agent3 (in the top right). 

```
pom_battle \
    --agents="test::agents.SimpleAgent,test::agents.SimpleAgent,test::agents.SimpleAgent,docker::pommerman/test-agent"
```
