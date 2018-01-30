import a
from flask import g, jsonify, request, url_for


@a.app.route("/api/get_agents/:slug", methods=["GET"])
def get_agents(slug):
    print('GET AGENTS: ', slug)
    user = a.models.User.get_by(slug=slug)
    if user:
        print("SUCC")
        return jsonify(agents=[agent.serialize() for agent in user.get_agents()])
    else:
        print("FAIL")
        error = "400 There is no user with that slug."
        return jsonify(error=error), error
