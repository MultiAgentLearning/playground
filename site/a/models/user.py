"""User

Object model:
- One-Many Agents
- Many-Many Competitions
- Name
- Email
"""
import a
from . import mixins


user_competitions = a.db.Table('user_competitions',
    a.db.Column('competition_id', a.db.Integer, a.db.ForeignKey('competition.id'), primary_key=True),
    a.db.Column('user_id', a.db.Integer, a.db.ForeignKey('user.id'), primary_key=True)
)


class User(a.db.Model, mixins.BaseModelMixin):
    id = a.db.Column(a.db.Integer(), primary_key=True)
    email = a.db.Column(a.db.String(255), unique=True)
    password = a.db.Column(a.db.String(255))
    agents = a.db.relationship('Agent', backref='user', lazy=True)
    competitions = a.db.relationship('Competition', secondary=user_competitions, lazy='subquery',
                                     backref=a.db.backref('users', lazy=True))

    def __init__(self, email, password):
        self.email = email
        self.active = True
        self.password = User.hashed_password(password)

    def serialize():
        ret = super().serialize()
        print("user: ", ret)
        return ret

    @staticmethod
    def hashed_password(password):
        bc = a.bcrypt.generate_password_hash(password)
        return a.bcrypt.generate_password_hash(password)

    @staticmethod
    def get_user_with_email_and_password(email, password):
        user = User.get_by(email=email)
        if user and a.bcrypt.check_password_hash(user.password, password):
            return user
        else:
            return None
