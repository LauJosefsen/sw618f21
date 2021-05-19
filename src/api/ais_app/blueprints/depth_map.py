import os

from dependency_injector.wiring import inject, Provide
from flask import Blueprint, send_file, request
from PIL import Image, ImageDraw
from tqdm import tqdm

from ais_app.containers import Container
from ais_app.services.depth_map_service import DepthMapService
from ais_app.services.enc_cell_service import EncCellService

blueprint = Blueprint("depth_map", __name__)


@blueprint.route("/raw/tile/<z>/<x>/<y>")
@inject
def get_tile(
    z,
    x,
    y,
    depth_map_service: DepthMapService = Provide[Container.depth_map_service],
):
    try:
        response = send_file(
            f"{depth_map_service.raw_tiles_folder}/{z}-{x}-{y}.png",
            mimetype="image/png",
        )
    except FileNotFoundError:
        response = send_file("blank.png", mimetype="image/png")
    return response


@blueprint.route("/raw/legend")
@inject
def get_legend(
    depth_map_service: DepthMapService = Provide[Container.depth_map_service],
):
    return send_file(
        f"{depth_map_service.raw_tiles_folder}/legend.svg", mimetype="image/svg+xml"
    )


@blueprint.route("/interpolated/tile/<z>/<x>/<y>")
@inject
def get_tile_interpolated(
    z,
    x,
    y,
    depth_map_service: DepthMapService = Provide[Container.depth_map_service],
):
    try:
        response = send_file(
            f"${depth_map_service.interpolated_tiles_folder}/{z}-{x}-{y}.png",
            mimetype="image/png",
        )
    except FileNotFoundError:
        response = send_file("blank.png", mimetype="image/png")
    return response


@blueprint.route("/interpolated/legend")
@inject
def get_legend_interpolated(
    depth_map_service: DepthMapService = Provide[Container.depth_map_service],
):
    return send_file(
        f"{depth_map_service.interpolated_tiles_folder}/legend.svg",
        mimetype="image/svg+xml",
    )


@blueprint.route("/raw/generate")
@inject
def generate_depth_map(
    depth_map_service: DepthMapService = Provide[Container.depth_map_service],
):
    min_zoom = request.args.get("min_zoom", default=7, type=int)
    max_zoom = request.args.get("max_zoom", default=9, type=int)

    do_generate = request.args.get("do_generate", default=True, type=bool)
    if do_generate:
        depth_map_service.generate_raw_depth_map()

    depth_map_service.render_raw_depth_map(min_zoom, max_zoom)

    return "Server go brbrbr"


@blueprint.route("/interpolated/generate")
@inject
def generate_depth_map_interpolated(
    depth_map_service: DepthMapService = Provide[Container.depth_map_service],
    enc_service: EncCellService = Provide[Container.enc_cell_service],
):
    enc_cell_id = request.args.get("enc_cell_id", default=110, type=int)
    grid_size = request.args.get(
        "grid_size", default=1000, type=int
    )  # todo hent fra db
    min_zoom = request.args.get("min_zoom", default=7, type=int)
    max_zoom = request.args.get("max_zoom", default=9, type=int)
    downscale = request.args.get("downscale", default=1, type=int)

    do_generate = request.args.get("do_generate", default=True, type=bool)
    if do_generate:
        enc_bounds = enc_service.get_enc_bounds_in_utm32n_by_id(enc_cell_id)
        depths, varians = depth_map_service.interpolate_depth_map_in_enc(
            enc_cell_id, enc_bounds, grid_size, downscale
        )
        depth_map_service.insert_interpolated_depth_map(
            enc_bounds, grid_size, depths, varians
        )

    depth_map_service.render_interpolated_depth_map(min_zoom, max_zoom)

    return "Ok"
