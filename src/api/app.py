from flask import Flask
from container import Container
import controller.ais_data_controller

container = Container()
app = Flask(__name__)
container.wire(modules=[controller.ais_data_controller])
app.container = container
app.add_url_rule('/', 'index', controller.ais_data_controller.index)


