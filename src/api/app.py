import controller.ais_data_controller
from container import Container
from flask import Flask

container = Container()
app = Flask(__name__)
container.wire(modules=[controller.ais_data_controller])
app.container = container
app.add_url_rule("/", "index", controller.ais_data_controller.index)
