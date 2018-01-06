import a
from flask import g, jsonify, request
from sqlalchemy.exc import IntegrityError


@a.app.route("/api/user", methods=["GET"])
@a.utils.auth.requires_auth
def get_user():
    return jsonify(result=g.current_user)


@a.app.route("/api/create_user", methods=["POST"])
def create_user():
    a.app.logger.info("YO")
    incoming = request.get_json()
    try:
        a.models.User.create(
            email=incoming["email"],
            password=incoming["password"]
        )
    except IntegrityError:
        return jsonify(message="User with that email already exists"), 409

    new_user = a.models.User.get_by(email=incoming["email"])

    return jsonify(
        id=new_user.id,
        token=a.utils.auth.generate_token(new_user)
    )


@a.app.route("/api/get_token", methods=["POST"])
def get_token():
    incoming = request.get_json()
    user = a.models.User.get_user_with_email_and_password(incoming["email"], incoming["password"])
    if user:
        return jsonify(token=a.utils.auth.generate_token(user))

    return jsonify(error=True), 403


@a.app.route("/api/is_token_valid", methods=["POST"])
def is_token_valid():
    incoming = request.get_json()
    is_valid = a.utils.auth.verify_token(incoming["token"])

    if is_valid:
        return jsonify(token_is_valid=True)
    else:
        return jsonify(token_is_valid=False), 403
