from dependency_injector.wiring import inject, Provide
from flask import Blueprint, request, jsonify

from ais_app.containers import Container
from ais_app.services.heatmap_service import HeatmapService

blueprint = Blueprint("heatmaps", __name__)

"""
@api {get} /heatmaps/point_density
@apiGroup Heatmaps
@apiDescription Get heatmap data for point density

@apiParam {number} enc_id The enc to which to get the heatmap for
@apiParam {string[]} ship_types The ship types to show on the heatmap

@apiSuccess {json} heatmap_data The heatmap data
"""
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

"""
@api {get} /heatmaps/traffic_density
@apiGroup Heatmaps
@apiDescription Get heatmap data for traffic density

@apiParam {number} enc_id The enc to which to get the heatmap for
@apiParam {string[]} ship_types The ship types to show on the heatmap

@apiSuccess {json} heatmap_data The heatmap data
"""
@blueprint.route("/traffic_density")
@inject
def traffic_density_heatmap(
    heatmap_service: HeatmapService = Provide[Container.heatmap_service],
):
    enc_cell_id = request.args.get("enc_cell_id", default=0, type=int)
    ship_types = request.args.get("ship_types", default="", type=str).split(",")

    return jsonify(heatmap_service.trafic_density_heatmap(enc_cell_id, ship_types))

"""
@api {get} /heatmaps/generate_traffic_density
@apiGroup Heatmaps
@apiDescription Generates the trafic density heatmap

@apiSuccess {bool} success True if succeeded
"""
@blueprint.route("/generate_traffic_density")
@inject
def generate_traffic_density_heatmap(
    heatmap_service: HeatmapService = Provide[Container.heatmap_service],
):
    heatmap_service.generate_traffic_density()
    return jsonify({"success": True})

"""
@api {get} /heatmaps/generate_point_density
@apiGroup Heatmaps
@apiDescription Generates the point density heatmap

@apiSuccess {bool} success True if succeeded
"""
@blueprint.route("/generate_point_density")
@inject
def generate_point_density_heatmap(
    heatmap_service: HeatmapService = Provide[Container.heatmap_service],
):
    heatmap_service.generate_point_density()
    return jsonify({"success": True})
