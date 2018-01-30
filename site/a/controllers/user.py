import a
from flask import g, jsonify, request, url_for
import requests
from sqlalchemy.exc import IntegrityError


@a.app.route("/api/user", methods=["GET"])
@a.utils.auth.requires_auth
def get_user():
    return jsonify(user=g.current_user.serialize())


@a.app.route("/api/create_user", methods=["POST"])
def create_user():
    incoming = request.get_json()
    email = incoming["email"]
    password = incoming["password"]
    try:
        new_user = a.models.User.create(
            name=incoming["name"],
            email=email,
            password=a.models.User.hashed_password(password)
        )
        new_user.set_slug(name=new_user.name)

        return jsonify(
            token=a.utils.auth.generate_token(new_user),
            user=new_user.serialize()
        )
    except IntegrityError:
        error = "409 User with that email already exists."
        return jsonify(error=error), error
    except Exception as e:
        user = a.models.User.get_user_with_email_and_password(email, password)
        if user:
            user.delete()
            a.db.session.commit()
        error = "500 Unknown error. Please try again."
        return jsonify(error=error), error


@a.app.route("/api/get_token", methods=["POST"])
def get_token():
    incoming = request.get_json()
    user = a.models.User.get_user_with_email_and_password(incoming["email"], incoming["password"])
    if user:
        return jsonify(token=a.utils.auth.generate_token(user))

    return jsonify(error=True), 403


@a.app.route('/logout')
def logout():
    session.pop('google_token', None)
    g.current_user = None
    return redirect(url_for('index'))


@a.app.route('/api/user/github_oauth', methods=["POST"])
def github_oauth():
    incoming = request.get_json()
    user = a.utils.auth.verify_token(incoming["token"])
    if not user:
        # TODO: This would be the scenario where we don't have a token, i.e. fresh user w Github.
        return jsonify(success=False), 403

    data = {
        'code': incoming['code'],
        'client_id': a.app.config['GITHUB_CLIENT_ID'],
        'client_secret': a.app.config['GITHUB_CLIENT_SECRET']
    }
    r = requests.post('https://github.com/login/oauth/access_token', json=data,
                      headers={'Content-type': 'application/json', 'Accept': 'text/plain'})

    return jsonify(success=True)
