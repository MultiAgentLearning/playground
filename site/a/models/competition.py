"""Competition

Object model:
- Many-Many Agents
- Name
- Date
- One-Many Battles
- Many-One Games

The Competition class's backrefs include:
- Competition.users
- Competition.game
"""
import a
from . import mixins
from sqlalchemy import DateTime


competition_agents = a.db.Table('competition_agents',
    a.db.Column('agent_id', a.db.Integer, a.db.ForeignKey('agent.id'), primary_key=True),
    a.db.Column('competition_id', a.db.Integer, a.db.ForeignKey('competition.id'), primary_key=True)
)


class Competition(a.db.Model, mixins.BaseModelMixin):
    id = a.db.Column(a.db.Integer(), primary_key=True)
    name = a.db.Column(a.db.String(255))
    date = a.db.Column(DateTime)
    agents = a.db.relationship('Agent', secondary=competition_agents, lazy='subquery',
                               backref=a.db.backref('competitions', lazy=True))
    battles = a.db.relationship('Battle', backref='competition', lazy=True)
    game_id = a.db.Column(a.db.Integer(), a.db.ForeignKey('game.id'), index=True)
    
