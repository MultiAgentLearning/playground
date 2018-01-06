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


if __name__ == '__main__':
    manager.run()
