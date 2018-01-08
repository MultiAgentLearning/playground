import a
from flask import g, redirect, request, url_for
from flask.ext.admin.contrib.sqla import ModelView


@a.app.before_request
def check_for_admin():
    print('CHECK FOR ADMIN')
    if request.path.startswith('/admin'):
        if not g.current_user or not g.current_user.is_admin:
            return redirect(url_for('home'))


class UserView(ModelView):
    column_list = ('name', 'email', 'is_email_validated', 'is_admin')

    def __init__(self, session, **kwargs):
        super(UserView, self).__init__(a.models.User, session, **kwargs)


class GameView(ModelView):
    column_list = ('name', 'config', 'slug')

    def __init__(self, session, **kwargs):
        super(GameView, self).__init__(a.models.Game, session, **kwargs)


a.admin.add_view(UserView(a.db.session))
a.admin.add_view(GameView(a.db.session))
