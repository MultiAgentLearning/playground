import datetime
import random

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
    db.session.commit()


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
    admin, _ = User.get_or_create(
        name='Test Admin', email='admin@email.com', is_email_validated=True,
        is_admin=True, password=User.hashed_password("password")
    )

    u1, _ = User.get_or_create(
        name='Pommer Man', email='u1@e.com', is_email_validated=True,
        is_admin=False, password=User.hashed_password('password')
    )

    a1, _ = Agent.get_or_create(
        name="MyPommermanAgent",
    )
    a2, _ = Agent.get_or_create(
        name="ReinforcedAgent",
    )
    u1.agents = [a1, a2]

    u2, _ = User.get_or_create(
        name='Pommer Woman', email='u2@e.com', is_email_validated=True,
        is_admin=False, password=User.hashed_password('password')
    )

    a3, _ = Agent.get_or_create(
        name="PomderWoman",
    )
    a4, _ = Agent.get_or_create(
        name="PommeranianPower",
    )
    a5, _ = Agent.get_or_create(
        name="PommePie",
    )
    u2.agents = [a3, a4, a5]

    u3, _ = User.get_or_create(
        name='Cptn Plantit', email='u3@e.com', is_email_validated=False,
        is_admin=False, password=User.hashed_password('password')
    )
    a6, _ = Agent.get_or_create(
        name="Kooperate",
    )
    a7, _ = Agent.get_or_create(
        name="TheCoup",
    )
    a8, _ = Agent.get_or_create(
        name="CopsAndPommers",
    )
    u3.agents = [a6, a7, a8]

    all_agents = [a1, a2, a3, a4, a5, a6, a7, a8]

    ffa_game, _ = Game.get_or_create(
        name="Pommerman FFA",
        config="https://github.com/hardmaru/playground/tree/master/games/a/pommerman/README.md",
        github_url="https://github.com/hardmaru/playground/tree/master/games/a/pommerman",
        scoring="4,3,2,1",
    )
    ffa_game.agents = all_agents

    team_game, _ = Game.get_or_create(
        name="Pommerman Team",
        config="https://github.com/hardmaru/playground/tree/master/games/a/pommerman/README.md",
        github_url="https://github.com/hardmaru/playground/tree/master/games/a/pommerman",
        scoring="1,0"
    )
    team_game.agents = all_agents

    team_radio_game, _ = Game.get_or_create(
        name="Pommerman Team Radio",
        config="https://github.com/hardmaru/playground/tree/master/games/a/pommerman/README.md",
        github_url="https://github.com/hardmaru/playground/tree/master/games/a/pommerman",
        scoring="1,0"
    )
    team_radio_game.agents = all_agents

    for i in range(5):
        ffa_players = random.sample(all_agents, 4)
        team_players = [random.choice(u2.agents) for _ in range(2)] + [random.choice(u1.agents) for _ in range(2)]
        team_radio_players = [random.choice(u3.agents) for _ in range(2)] + [random.choice(u2.agents) for _ in range(2)]
        make_battle(ffa_players, ffa_game)
        make_battle(team_players, team_game)
        make_battle(team_radio_players, team_radio_game)

    db.session.commit()


def make_battle(agents, game):
    b1, _ = Battle.get_or_create(date=datetime.datetime.utcnow() - datetime.timedelta(days=random.randint(0, 10)))
    b1.agents = agents
    b1.game = game
    scoring = [float(k) for k in game.scoring.split(',')]
    if len(scoring) == 2:
        scoring = [scoring[0]]*2 + [scoring[1]]*2

    for _agent, _score in zip(b1.agents, scoring):
        score = Score(_score)
        score.battle = b1
        score.agent = _agent

        
if __name__ == '__main__':
    manager.run()
