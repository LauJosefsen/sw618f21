import os

from dependency_injector.wiring import inject, Provide
from flask import Blueprint, send_file, request, jsonify
from PIL import Image, ImageDraw
from tqdm import tqdm

from ais_app.containers import Container
from ais_app.services.depth_map_service import DepthMapService
from ais_app.services.enc_cell_service import EncCellService

blueprint = Blueprint("depth_map", __name__)

"""
@api {get} /depth_map/raw/tile/:z/:x/:y
@apiGroup Depth map
@apiDescription Gets a specified tile for raw depthmap.

@apiSuccess {image/png} image The requested tile
"""


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


"""
@api {get} /depth_map/raw/legend
@apiGroup Depth map
@apiDescription Get the legend for the raw depthmap

@apiSuccess {image/svg} image The color legend
"""


@blueprint.route("/raw/legend")
@inject
def get_legend(
    depth_map_service: DepthMapService = Provide[Container.depth_map_service],
):
    return send_file(
        f"{depth_map_service.raw_tiles_folder}/legend.svg", mimetype="image/svg+xml"
    )


"""
@api {get} /depth_map/interpolated/tile/:z/:x/:y
@apiGroup Depth map
@apiDescription Gets a specified tile for the interpolated depthmap.

@apiSuccess {image/png} image The requested tile
"""


@blueprint.route("/interpolated/tile/<z>/<x>/<y>")
@inject
def get_tile_interpolated(
    z,
    x,
    y,
    depth_map_service: DepthMapService = Provide[Container.depth_map_service],
):
    print(os.path.join(os.getcwd(), f"{depth_map_service.interpolated_tiles_folder}/{z}-{x}-{y}.png"))
    try:
        response = send_file(
            f"{depth_map_service.interpolated_tiles_folder}/{z}-{x}-{y}.png",
            mimetype="image/png",
        )
    except FileNotFoundError:
        response = send_file("blank.png", mimetype="image/png")
    return response


"""
@api {get} /depth_map/interpolated/legend
@apiGroup Depth map
@apiDescription Get the legend for the interpolated depthmap

@apiSuccess {image/svg} image The color legend
"""


@blueprint.route("/interpolated/legend")
@inject
def get_legend_interpolated(
    depth_map_service: DepthMapService = Provide[Container.depth_map_service],
):
    return send_file(
        f"{depth_map_service.interpolated_tiles_folder}/legend.svg",
        mimetype="image/svg+xml",
    )


"""
@api {get} /depth_map/raw/generate
@apiGroup Depth map
@apiDescription Generates the raw depthmap and its tiles

@apiParam {number} min_zoom The minimum zoom level to render tiles to
@apiParam {number} max_zoom The maximum zoom level to render tiles to
@apiParam {number} do_generate If set to 1, then does generation

@apiSuccess {bool} success True if succeeded
"""


@blueprint.route("/raw/generate")
@inject
def generate_depth_map(
    depth_map_service: DepthMapService = Provide[Container.depth_map_service],
):
    min_zoom = request.args.get("min_zoom", default=7, type=int)
    max_zoom = request.args.get("max_zoom", default=9, type=int)

    do_generate = request.args.get("do_generate", default=0, type=bool)
    if do_generate == 1:
        depth_map_service.generate_raw_depth_map()

    depth_map_service.render_raw_depth_map(min_zoom, max_zoom)

    return jsonify({"success": True})


"""
@api {get} /depth_map/interpolated/generate
@apiGroup Depth map
@apiDescription Generates the raw depthmap and its tiles

@apiParam {number} enc_cell_id The enc cell to render it for.
@apiParam {number} min_zoom The minimum zoom level to render tiles to
@apiParam {number} max_zoom The maximum zoom level to render tiles to
@apiParam {number} downscale If set to more than 1, it will downscale the raw depth map by this factor in both x-y before interpolating.
@apiParam {number} do_generate If set to 1, then does generation

@apiSuccess {bool} success True if succeeded
"""


@blueprint.route("/interpolated/generate")
@inject
def generate_depth_map_interpolated(
    depth_map_service: DepthMapService = Provide[Container.depth_map_service],
    enc_service: EncCellService = Provide[Container.enc_cell_service],
):
    enc_cell_id = request.args.get("enc_cell_id", default=140, type=int)
    min_zoom = request.args.get("min_zoom", default=7, type=int)
    max_zoom = request.args.get("max_zoom", default=13, type=int)
    downscale = request.args.get("downscale", default=1, type=int)
    do_generate = request.args.get("do_generate", default=0, type=bool)

    grid_size = 500 #todo make automatic

    if do_generate == 1:
        enc_bounds = enc_service.get_enc_bounds_in_utm32n_by_id(enc_cell_id)
        depths, varians = depth_map_service.interpolate_depth_map_in_enc(
            enc_cell_id, enc_bounds, grid_size, downscale
        )
        depth_map_service.insert_interpolated_depth_map(
            enc_bounds, grid_size, depths, varians
        )

    depth_map_service.render_interpolated_depth_map(min_zoom, max_zoom)

    return jsonify({"success": True})
