"""Score

Object model:
- Many-One Battle
- Many-One Agent
- Value

The Score class's backrefs include:
- Score.battle
- Score.agent
"""
import a
from . import mixins
from sqlalchemy import DateTime


class Score(a.db.Model, mixins.BaseModelMixin):
    id = a.db.Column(a.db.Integer(), primary_key=True)
    battle_id = a.db.Column(a.db.Integer(), a.db.ForeignKey('battle.id'), index=True)
    agent_id = a.db.Column(a.db.Integer(), a.db.ForeignKey('agent.id'), index=True)
    value = a.db.Column(a.db.Float)

    def __init__(self, value):
        self.value = value

