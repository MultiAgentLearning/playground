import a
from flask import render_template


@a.app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@a.app.route('/<path:path>', methods=['GET'])
def any_root_path(path):
    return render_template('index.html')

