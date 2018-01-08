"""Battle

Object model:
- Many-Many Agents
- Date
- Many-One Competition
- One-Many Scores

The Battle class's backrefs include:
- Battle.competition
"""
import a
from . import mixins
from sqlalchemy import DateTime


battle_agents = a.db.Table('battle_agents',
    a.db.Column('agent_id', a.db.Integer, a.db.ForeignKey('agent.id'), primary_key=True),
    a.db.Column('battle_id', a.db.Integer, a.db.ForeignKey('battle.id'), primary_key=True)
)

class Battle(a.db.Model, mixins.BaseModelMixin):
    id = a.db.Column(a.db.Integer(), primary_key=True)
    date = a.db.Column(DateTime)
    agents = a.db.relationship('Agent', secondary=battle_agents, lazy='subquery',
                               backref=a.db.backref('battles', lazy=True))
    competition_id = a.db.Column(a.db.Integer(), a.db.ForeignKey('competition.id'), index=True)


