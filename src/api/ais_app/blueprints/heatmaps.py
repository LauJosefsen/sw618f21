from dependency_injector.wiring import inject, Provide
from flask import Blueprint, request, jsonify

from ais_app.containers import Container
from ais_app.services.heatmap_service import HeatmapService

blueprint = Blueprint("heatmaps", __name__)


@blueprint.route("/point_density")
@inject
def point_density_heatmap(
    heatmap_service: HeatmapService = Provide[Container.heatmap_service],
):
    enc_cell_id = request.args.get("enc_cell_id", default=0, type=int)
    ship_types = request.args.get("ship_types", default="", type=str).split(",")

    return jsonify(
        heatmap_service.point_density_heatmap(enc_cell_id, ship_types=ship_types)
    )


@blueprint.route("/traffic_density")
@inject
def traffic_density_heatmap(
    heatmap_service: HeatmapService = Provide[Container.heatmap_service],
):
    enc_cell_id = request.args.get("enc_cell_id", default=0, type=int)
    ship_types = request.args.get("ship_types", default="", type=str).split(",")

    return jsonify(heatmap_service.trafic_density_heatmap(enc_cell_id, ship_types))


@blueprint.route("/generate_traffic_density")
@inject
def generate_traffic_density_heatmap(
    heatmap_service: HeatmapService = Provide[Container.heatmap_service],
):
    heatmap_service.generate_traffic_density()
    return "Ok"


@blueprint.route("/generate_point_density")
@inject
def generate_point_density_heatmap(
    heatmap_service: HeatmapService = Provide[Container.heatmap_service],
):
    heatmap_service.generate_point_density()
    return "Ok"
