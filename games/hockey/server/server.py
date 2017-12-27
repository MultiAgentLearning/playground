"""Simple Flask server for local JS rendering."""

from flask import Flask
from flask import request
from flask import render_template
from flask.ext.cors import CORS
from flask import jsonify

app = Flask(__name__, template_folder='template', static_folder='static')
CORS(app)
app.debug = True


@app.route('/', methods=['GET'])
def highway():
    return render_template('render.html')


data = []
@app.route('/write', methods=['POST'])
def write():
    global data
    close = request.json['close']
    if not close:
        data.append(request.json)
    return jsonify(result=True)


@app.route('/read', methods=['GET'])
def read():
    ret = {}
    if len(data) == 1:
        ret = data[0]
    elif len(data) > 1:
        ret = data.pop(0)
    return jsonify(ret)


if __name__ == "__main__":
    app.run(host="0.0.0.0")
