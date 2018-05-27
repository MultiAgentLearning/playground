# TODO: Add Documentation.

import os
import random
import shutil
import sys
import time
import traceback

import docker
from celery import Celery
import requests
import subprocess

sys.path.insert(1, os.path.join(sys.path[0], '..'))
import pommerman

client = docker.from_env()
client.login(os.getenv("PLAYGROUND_DOCKER_LOGIN"), os.getenv("PLAYGROUND_DOCKER_PASSWORD"))
celery = Celery("playground")
celery.conf.broker_url = 'redis://localhost:6379/0'


@celery.task
def run_test(docker_build_path, github_repo, private_key, name, agent_id, user, config):
    user = user.lower()
    name = name.lower()
    img = None
    message = None

    for func in [
            lambda: save_ssh_pk(name, private_key),
            lambda: download_repo(name, github_repo),
            lambda: docker_build(docker_build_path, name, user),
            lambda: battle(name, user, 5, config)
    ]:
        # TODO: This convoluted process might not be necessary if we can fix the image purging.
        is_success, ret = func()
        if type(ret) == docker.models.images.Image:
            img = ret
        else:
            message = ret

        if not is_success:
            return fail_test(agent_id, ret)

    # This has been successful. Hurray.
    # Push the Docker image to the cloud and then clean it up.
    docker_push_and_clean_up(img, name, user)
    return pass_test(agent_id, message)

# TODO: Add logging in case the post fails.
# TODO: This needs auth.
def fail_test(agent_id, error):
    """Sends ping to server that this was a failed test."""
    request_url = os.getenv('PLAYGROUND_SERVER_URL' + '/fail_test')
    requests.post(request_url, json={
        "agent_id": agent_id,
        "error": error,
        "access": os.getenv('PLAYGROUND_GAME_MANAGER_ACCESS')
    })

# TODO: Add logging in case the post fails.
# TODO: This needs auth.
def pass_test(agent_id, win_percent):
    """Sends ping that this was a successful test."""
    request_url = os.getenv('PLAYGROUND_SERVER_URL' + '/fail_test')
    requests.post(request_url, json={
        "agent_id": agent_id,
        "win_percent": win_percent,
        "access": os.getenv('PLAYGROUND_GAME_MANAGER_ACCESS')
    })

def save_ssh_pk(name, private_key):
    try:
        path = os.path.expanduser('~/.ssh/id_%s' % name)
        if os.path.exists(path):
            os.remove(path)

        with os.fdopen(os.open(path, os.O_WRONLY | os.O_CREAT, 0o600), 'w') as f:
            f.write(private_key)

        return True, ""
    except Exception as e:
        return False, "save_ssh_pk: %s" % e

def download_repo(name, github_repo):
    try:
        directory = os.path.expanduser('~/Repos/%s' % name)
        if os.path.exists(directory):
            shutil.rmtree(directory)

        from git import Repo
        from git import Git

        git_ssh_identity_file = os.path.expanduser('~/.ssh/id_%s' % name)
        git_ssh_cmd = 'ssh -i %s' % git_ssh_identity_file
        Repo.clone_from(github_repo, directory, env={'GIT_SSH_COMMAND': git_ssh_cmd})
        return True, ""
    except Exception as e:
        return False, "download_repo: %s" % e

def docker_build(docker_build_path, name, user):
    try:
        repo_path = os.path.join(os.path.expanduser('~/Repos'), name)
        img = client.images.build(path=repo_path, dockerfile=docker_build_path, tag='%s-%s' % (user, name))
        return True, img
    except Exception as e:
        return False, "docker_build: %s" % e

def battle(name, user, num_times, config):
    try:
        agents = "test::a.pommerman.agents.SimpleAgent,test::a.pommerman.agents.SimpleAgent,test::a.pommerman.agents.SimpleAgent".split(",")
        agent_id = random.randint(0, len(agents))
        agents.insert(agent_id, "docker::%s/%s" % (user, name))

        infos = []
        infos = pommerman.cli.run_battle.run(game='pommerman', config=config, agents=",".join(agents), record_dir=None, num_times=num_times)
        win_count = len([i for i in infos if 'winners' in i and agent_id in i['winners']])
        win_percent = 1. * win_count / len(infos)
        return True, win_percent
    except Exception as e:
        return False, "battle: %s" % e

def docker_push_and_clean_up(img, name, user):
    try:
        client.images.push("multiagentlearning/pommerman", tag="%s-%s" % (user, name))
        # TODO: Fix this so that it purges correctly. 
        client.images.remove("%s-%s" % (user, name))
        return True
    except Exception as e:
        print("push / clean up: ", e)
        return False
