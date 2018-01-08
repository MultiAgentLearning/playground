"""Game: Represents the environment used, e.g. Bridge.

A single game can spawn lots of Competitions.

Object model:
- One-Many Competitions
- Name
- Config: This is the configuration used to setup the game environment.
"""
import a
from . import mixins


class Game(a.db.Model, mixins.BaseModelMixin, mixins.SlugMixin):
    id = a.db.Column(a.db.Integer(), primary_key=True)
    name = a.db.Column(a.db.String(255))
    config = a.db.Column(a.db.String(255))
    competitions = a.db.relationship('Competition', backref='game', lazy=True)
