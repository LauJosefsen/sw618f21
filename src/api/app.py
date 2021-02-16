from flask import Flask

app = Flask(__name__)


@app.route("/")
def index():
    meh = [x for x in range(1, 30)]
    return {'hva': meh}
