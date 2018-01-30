"""Game: Represents the environment used, e.g. Bridge.

A single game can spawn lots of Competitions.

Object model:
- One-Many Competitions
- Name
- Config: This is the configuration used to setup the game environment.
- One-Many Battles

The Game class's backrefs include:
- Game.agents (all agents that have been played in this game.)
"""
import a
from . import mixins


class Game(a.db.Model, mixins.BaseModelMixin, mixins.SlugMixin):
    id = a.db.Column(a.db.Integer(), primary_key=True)
    name = a.db.Column(a.db.String(255))
    config = a.db.Column(a.db.String(255))
    github_url = a.db.Column(a.db.String(255))
    competitions = a.db.relationship('Competition', backref='game', lazy=True)
    battles = a.db.relationship('Battle', backref='game', lazy=True)
    # Scoring is a comma delineated string of floats representing the scores for the winners.
    # An example would be 4,3,2,1 for Pommerman FFA or 1,0 for Pommerman team.
    scoring = a.db.Column(a.db.Text)
