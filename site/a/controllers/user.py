import a
from flask import g, jsonify, request, url_for
import requests
from sqlalchemy.exc import IntegrityError


@a.app.route("/api/user", methods=["GET"])
@a.utils.auth.requires_auth
def get_user():
    return jsonify(result=g.current_user.serialize())


@a.app.route("/api/create_user", methods=["POST"])
def create_user():
    incoming = request.get_json()
    try:
        new_user = a.models.User.create(
            email=incoming["email"],
            password=a.models.User.hashed_password(incoming["password"])
        )
        return jsonify(
            token=a.utils.auth.generate_token(new_user)
        )
    except IntegrityError:
        return jsonify(message="User with that email already exists"), 409


@a.app.route("/api/get_token", methods=["POST"])
def get_token():
    incoming = request.get_json()
    user = a.models.User.get_user_with_email_and_password(incoming["email"], incoming["password"])
    if user:
        return jsonify(token=a.utils.auth.generate_token(user))

    return jsonify(error=True), 403


@a.app.route("/api/is_token_valid", methods=["POST"])
def is_token_valid():
    print('wat')
    incoming = request.get_json()
    is_valid = a.utils.auth.verify_token(incoming["token"])

    if is_valid:
        print("ITV Y")
        return jsonify(token_is_valid=True)
    else:
        print("ITV N")
        return jsonify(token_is_valid=False), 403


@a.app.route("/api/google_oauth")#, methods=["POST"])
def google_oauth():
    a.app.logger.info("LOG: GOOG OAUTH!!")
    print("print: GOOG OAUTH!! : ", a.app.config['GOOGLE_REDIRECT_URI'])
    ret = a.google.authorize(callback=url_for('google_authorized'), _external=True)
    print(ret)
    return ret


@a.app.route(a.app.config['GOOGLE_REDIRECT_URI'])
def google_authorized(resp):
    print('GOOG AUTH')
    resp = a.google.authorized_response()
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )
    session['google_token'] = resp['access_token']
    user = google.get('userinfo')
    print("GOOGLE USER: ", user)
    # Create or get user
    # user = a.models.User.get_or_create(**kwargs)
    # g.current_user = user
    return jsonify(data=g.current_user.serialize())


@a.google.tokengetter
def get_google_oauth_token():
    return session.get('google_token')


@a.app.route('/logout')
def logout():
    session.pop('google_token', None)
    g.current_user = None
    return redirect(url_for('index'))


@a.app.route('/api/user/github_oauth', methods=["POST"])
def github_oauth():
    print("FALAFLE") 
    incoming = request.get_json()
    print(incoming)
    user = a.utils.auth.verify_token(incoming["token"])
    if not user:
        # TODO: This would be the scenario where we don't have a token, i.e. fresh user w Github.
        return jsonify(success=False), 403

    print("GH Oauth: ", user)
    data = {
        'code': incoming['code'],
        'client_id': a.app.config['GITHUB_CLIENT_ID'],
        'client_secret': a.app.config['GITHUB_CLIENT_SECRET']
    }
    print(data)
    r = requests.post('https://github.com/login/oauth/access_token', json=data,
                      headers={'Content-type': 'application/json', 'Accept': 'text/plain'})
    print(r.status_code)
    print(r.json())
    
    return jsonify(success=True)
    

