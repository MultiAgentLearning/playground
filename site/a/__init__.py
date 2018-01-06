from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import logging
from logging.handlers import RotatingFileHandler
import os


class BaseConfig(object):
    SECRET_KEY = os.environ['PLAYGROUND_SECRET_KEY']
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ['PLAYGROUND_DATABASE_URL']
    SQLALCHEMY_TRACK_MODIFICATIONS = True


app = Flask(__name__, static_folder="./static/dist", template_folder="./static")
app.config.from_object(BaseConfig)

handler = RotatingFileHandler('./logs/app.log', maxBytes=10000, backupCount=1)
handler.setLevel(logging.INFO)
app.logger.addHandler(handler)

db = SQLAlchemy(app)

bcrypt = Bcrypt(app)

from . import utils
from . import models
from . import controllers
