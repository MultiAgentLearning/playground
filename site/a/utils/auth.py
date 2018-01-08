import a
from functools import wraps
from flask import request, g, jsonify, session
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import SignatureExpired, BadSignature

TWO_WEEKS = 1209600


def generate_token(user, expiration=TWO_WEEKS):
    s = Serializer(a.app.config['SECRET_KEY'], expires_in=expiration)
    token = s.dumps({'id': user.id, 'email': user.email}).decode('utf-8')
    return token


def verify_token(token):
    s = Serializer(a.app.config['SECRET_KEY'])
    try:
        data = s.loads(token)
        if 'id' not in data or 'email' not in data:
            return None

        user = a.models.User.get(data['id'])
        if data['email'] != user.email:
            return None

        return user
    except (BadSignature, SignatureExpired):
        return None


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization', None)
        if token:
            string_token = token.encode('ascii', 'ignore')
            user = verify_token(string_token)

            if user and 'google_token' in session:
                google_info = a.google.get('userinfo')
                print("GOOG INFO: ", google_info)
                # TODO: Ensure that Google OAuth has not been revoked.
            
            if user:
                g.current_user = user
                return f(*args, **kwargs)
        return jsonify(message="Authentication is required to access this resource"), 401

    return decorated
