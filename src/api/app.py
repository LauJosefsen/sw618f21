import controller.ais_data_controller
from container import Container
from flask import Flask, request
from datetime import datetime
import yappi
import atexit


# End profiling and save the results into file
def output_profiler_stats_file():
    profile_file_name = (
        "yappi." + datetime.now().isoformat().replace(":", ".") + ".pstat"
    )
    func_stats = yappi.get_func_stats()
    func_stats.save(profile_file_name, type="pstat")
    yappi.stop()
    yappi.clear_stats()


yappi.start()
atexit.register(output_profiler_stats_file)

container = Container()
app = Flask(__name__)
container.wire(modules=[controller.ais_data_controller])
app.container = container

app.add_url_rule("/", "index", controller.ais_data_controller.index)
app.add_url_rule("/import", "import", controller.ais_data_controller.import_ais_data)
app.add_url_rule("/tracks", "get_routes", controller.ais_data_controller.get_tracks)
app.add_url_rule(
    "/import_enc", "import_enc", controller.ais_data_controller.import_enc_data
)
app.add_url_rule(
    "/get_enc_cells", "get_enc_cells", controller.ais_data_controller.get_enc_cells
)

app.add_url_rule(
    "/cluster-points", "cluster_points", controller.ais_data_controller.cluster_points
)

app.add_url_rule(
    "/cluster-heatmap",
    "cluster_heatmap",
    controller.ais_data_controller.cluster_heatmap,
)
app.add_url_rule(
    "/find_ais_time_median", "find_ais_time_median", controller.ais_data_controller.find_ais_time_median
)

def shutdown_server():
    func = request.environ.get("werkzeug.server.shutdown")
    if func is None:
        raise RuntimeError("Not running with the Werkzeug Server")
    func()


@app.route("/shutdown", methods=["GET"])
def shutdown():
    shutdown_server()
    return "Server shutting down..."


@app.after_request  # blueprint can also be app~~
def after_request(response):
    header = response.headers
    header["Access-Control-Allow-Origin"] = "*"  # todo vulnerable to xss
    return response
