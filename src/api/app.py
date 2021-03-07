import controller.ais_data_controller
from container import Container
from flask import Flask


if __name__ == "__main__":
    container = Container()
    app = Flask(__name__)
    container.wire(modules=[controller.ais_data_controller])
    app.container = container

    app.add_url_rule("/", "index", controller.ais_data_controller.index)
    app.add_url_rule("/import", "import", controller.ais_data_controller.import_ais_data)
    app.add_url_rule("/routes", "get_routes", controller.ais_data_controller.get_routes)
    app.add_url_rule(
        "/cluster-points", "cluster_points", controller.ais_data_controller.cluster_points
    )
