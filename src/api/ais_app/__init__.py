from datetime import datetime

from flask import Flask

from .blueprints import data_management, enc_cells, heatmaps, tracks, depth_map
from .containers import Container
from simplejson import JSONEncoder

# https://stackoverflow.com/a/56562567
class DateTimeEncoder(JSONEncoder):
    def default(self, z):
        if isinstance(z, datetime):
            return str(z)
        else:
            return super().default(z)


container = Container()
container.wire(modules=[data_management, enc_cells, heatmaps, tracks, depth_map])

app = Flask(__name__)
app.container = container
app.register_blueprint(data_management.blueprint, url_prefix="/data_management")
app.register_blueprint(enc_cells.blueprint, url_prefix="/enc")
app.register_blueprint(heatmaps.blueprint, url_prefix="/heatmaps")
app.register_blueprint(tracks.blueprint, url_prefix="/tracks")
app.register_blueprint(depth_map.blueprint, url_prefix="/depth_map")
app.json_encoder = DateTimeEncoder


@app.route("/")
def index():
    return "Ok"


@app.after_request
def after_request(response):
    header = response.headers
    header["Access-Control-Allow-Origin"] = "*"
    return response
