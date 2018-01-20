import os
import random
import socket
from flask import jsonify

from flask import Flask, request


app = Flask(__name__)

@app.route("/action", methods=["POST"])
def action():
    data = request.get_json()
    obs = data.get("obs")
    ret = random.randint(0, 5)
    print(ret)
    print(obs)
    return jsonify({"action": ret})

@app.route("/")
def test():
    html = "<h3>Hello {name}!</h3>" \
           "<b>Hostname:</b> {hostname}<br/>"
    return html.format(name=os.getenv("NAME", "world"), hostname=socket.gethostname())

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)
