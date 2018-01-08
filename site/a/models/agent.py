"""Agent

Object model:
- Many-One User
- Many-Many Competitions
- Many-Many Battles
- Many-Many Games
- Name
- Date

The Agent class's backrefs include:
- Agent.battles
- Agent.competitions
- Agent.user
"""
import a
from . import mixins

 
agent_games = a.db.Table('agent_games',
    a.db.Column('game_id', a.db.Integer, a.db.ForeignKey('game.id'), primary_key=True),
    a.db.Column('agent_id', a.db.Integer, a.db.ForeignKey('agent.id'), primary_key=True)
)


class Agent(a.db.Model, mixins.BaseModelMixin):
    id = a.db.Column(a.db.Integer(), primary_key=True)
    name = a.db.Column(a.db.String(255))
    user_id = a.db.Column(a.db.Integer(), a.db.ForeignKey('user.id'), index=True)
    games = a.db.relationship('Game', secondary=agent_games, lazy='subquery',
                              backref=a.db.backref('games', lazy=True))

