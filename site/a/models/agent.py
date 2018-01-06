"""Agent

Object model:
- Many-One User
- Many-Many Competitions
- Many-Many Battles
- Name
- Date

The Agent class's backrefs include:
- Agent.battles
- Agent.competitions
- Agent.user
"""
import a
from . import mixins


class Agent(a.db.Model, mixins.BaseModelMixin):
    id = a.db.Column(a.db.Integer(), primary_key=True)
    name = a.db.Column(a.db.String(255))
    user_id = a.db.Column(a.db.Integer(), a.db.ForeignKey('user.id'), nullable=False)
