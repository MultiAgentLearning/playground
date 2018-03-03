import os

import celery_ as celery
from flask import Flask, jsonify, request

app = Flask(__name__)

# TODO: Make this secure.
@app.route('/ping', methods=['GET'])
def ping():
    return jsonify(success=True)

# TODO: Make this secure.
@app.route('/test', methods=['POST'])
def test():
    try:
        incoming = request.get_json()
        if 'access' not in incoming or incoming['access'] != os.getenv('PLAYGROUND_GAME_MANAGER_ACCESS'):
            return jsonify(received=False, error="Access Denied"), 400

        docker_build_path = incoming["docker_build_path"]
        github_repo = incoming["github_repo"]
        private_key = incoming["private_key"]
        name = incoming["name"]
        agent_id = incoming["agent_id"]
        user = incoming["user"]
        config = incoming["config"]
        celery.run_test(docker_build_path, github_repo, private_key, name, agent_id, user, config)
        return jsonify(received=True, error="")
    except Exception as e:
        return jsonify(received=False, error=e)


if __name__ == '__main__':
    app.run()
