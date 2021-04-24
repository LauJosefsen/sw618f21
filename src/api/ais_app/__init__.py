from flask import Flask

from ais_app.services.ais_data_service import AisDataService
from .blueprints import enc_cells
from .containers import Container

container = Container()
container.wire(modules=[enc_cells])

app = Flask(__name__)
app.container = container
app.register_blueprint(enc_cells.blueprint, url_prefix="/enc")


@app.route("/")
def index():
    return "Ok"


@app.after_request
def after_request(response):
    header = response.headers
    header["Access-Control-Allow-Origin"] = "localhost:3000,app.techsource.dk"
    return response
