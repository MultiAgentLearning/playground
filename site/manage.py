from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

from a import app, db
from a.models import *

migrate = Migrate(app, db)
manager = Manager(app)

# migrations
manager.add_command('db', MigrateCommand)


@manager.command
def create_db():
    """Creates the db tables."""
    db.create_all()


@manager.command
def drop_db():
    db.drop_all()
    db.session.commit()


@manager.command
def initialize():
    """
    From a fresh setup:
    - creates the database.
    - makes a user.
    - makes an agent for that user.
    """

    # Create the database
    print('Making the database')
    db.create_all()
    db.session.commit()
    print('Completed making the database')

    # Make user with name:'User Person', password:'password', email:'admin@email.com'
    print('Making an admin test user with name "Test Admin", email "admin@email.com", ',
          'and password "password"')
    u, created = User.get_or_create(
        name='Test Admin', email='admin@email.com', is_email_validated=True,
        is_admin=True, password=User.hashed_password("password")
    )

    g, created = Game.get_or_create(
        name="Bomberman",
        config="https://github.com/hardmaru/playground/blob/master/games/bombergrid/README.md",
        github_url="https://github.com/hardmaru/playground/tree/master/games/bombergrid"
    )

    a, created = Agent.get_or_create(
        name="MyBombermanAgent",
    )
    u.agents.append(a)

    db.session.commit()


if __name__ == '__main__':
    manager.run()
