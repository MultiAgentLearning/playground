import a
from flask import jsonify


@a.app.route("/api/gamesXo/get/<slug>", methods=["GET"])
def get_game(slug):
    try:
        game = a.models.Game.get_by(slug=slug)
        if not game:
            return jsonify(success=False)
    except ValueError, e:
        return jsonify(success=False)

    ret = game.serialize()
    print(ret)
    return jsonify(success=True, game=ret)


@a.app.route("/api/games", methods=["GET"])
def get_games():
    try:
        games = a.models.Game.all()
        games = [game.serialize() for game in games]
        return jsonify(success=True, games=games)
    except ValueError, e:
        return jsonify(success=False)
