import config
from flask import Flask
from flask.ext.admin import Admin
from flask.ext.cache import Cache
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_oauthlib.client import OAuth
from flask_sqlalchemy import SQLAlchemy
import logging
import os


app = Flask(__name__, static_folder="./static/dist", template_folder="./static")
app.config.from_object('config.' + os.getenv('PLAYGROUND_CONFIG'))
print(app.config)

CORS(app)
logging.getLogger('flask_cors').level = logging.DEBUG

admin = Admin(name="flaskAdmin")
admin.init_app(app)

cache = Cache(app, config=app.config['CACHE_CONFIG'])

db = SQLAlchemy(app)

bcrypt = Bcrypt(app)

oauth = OAuth(app)
google = oauth.remote_app(
    'google',
    consumer_key=app.config.get('GOOGLE_CLIENT_ID'),
    consumer_secret=app.config.get('GOOGLE_CLIENT_SECRET'),
    request_token_params={
        'scope': 'email'
    },
    base_url='https://www.googleapis.com/oauth2/v1/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
)

from . import utils
from . import models
from . import controllers

