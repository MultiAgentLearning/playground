# playground
experiments with multiagent training


### Run a Docker agent

```bash
# Build the test agent
docker build -t pommerman/test-agent . -f games/a/docker/Dockerfile 

# Run with Docker agents
DOCKER_AGENT_AGENT_CLASS=a.docker.pommerman.simple_agent.agent.Agent \
python games/run_battle.py \
    --agents="random::null,random::null,random::null,docker::pommerman/test-agent"

```
