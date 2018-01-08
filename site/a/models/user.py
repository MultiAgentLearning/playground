"""User

Object model:
- One-Many Agents
- Many-Many Competitions
- Name
- Email
"""
import a
from . import mixins

# from flask.ext.login import UserMixin


user_competitions = a.db.Table('user_competitions',
    a.db.Column('competition_id', a.db.Integer, a.db.ForeignKey('competition.id'), primary_key=True),
    a.db.Column('user_id', a.db.Integer, a.db.ForeignKey('user.id'), primary_key=True)
)


class User(a.db.Model, mixins.BaseModelMixin):
    include_keys = ['email', 'name', 'is_admin', 'is_email_validated']

    id = a.db.Column(a.db.Integer(), primary_key=True)
    email = a.db.Column(a.db.Text, unique=True)
    name = a.db.Column(a.db.Text)
    password = a.db.Column(a.db.String(255))
    is_active = a.db.Column(a.db.Boolean, default=True)
    is_admin = a.db.Column(a.db.Boolean, default=False)
    agents = a.db.relationship('Agent', backref='user', lazy=True)
    competitions = a.db.relationship('Competition', secondary=user_competitions, lazy='subquery',
                                     backref=a.db.backref('users', lazy=True))
    email_validations = a.db.relationship('EmailValidation', backref='user', lazy='dynamic')
    email_validation_code = a.db.Column(a.db.String(20), index=True)
    is_email_validated = a.db.Column(a.db.Boolean, default=False)

    def serialize(self):
        ret = super().serialize()
        print("user: ", ret)
        ret['name'] = ret['name'].split(' ')[0]
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
