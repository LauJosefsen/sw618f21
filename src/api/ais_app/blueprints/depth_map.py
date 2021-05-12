from dependency_injector.wiring import inject, Provide
from flask import Blueprint, send_file
from PIL import Image, ImageDraw

from ais_app.containers import Container
from ais_app.services.depth_map_service import DepthMapService

blueprint = Blueprint("depth_map", __name__)


@blueprint.route("/tile/<z>/<x>/<y>")
def get_tile(z, x, y):
    try:
        response = send_file(f"tiles/{z}-{x}-{y}.png", mimetype="image/png")
    except FileNotFoundError:
        response = send_file("blank.png", mimetype="image/png")
    return response


def map(
    x: float, in_min: float, in_max: float, out_min: float, out_max: float
) -> float:
    """
    Maps a float from one interval to another
    :param x: The value to map
    :param in_min: The original value's interval minimum
    :param in_max: The original value's interval maximum
    :param out_min: The new interval minimum
    :param out_max: The new interval maximum
    :return: the mapped value in the new interval
    """
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


@blueprint.route("/generate/<min_zoom>/<max_zoom>")
@inject
def generate_depth_map(
    min_zoom,
    max_zoom,
    depth_map_service: DepthMapService = Provide[Container.depth_map_service],
):
    tiles = depth_map_service.get_map_tiles(min_zoom, max_zoom)
    max_depth = depth_map_service.get_max_depth()

    for tile in tiles:
        coordinates = tile["geom"]["coordinates"][0]
        tile_n = max(coordinates, key=lambda x: x[1])[1]
        tile_s = min(coordinates, key=lambda x: x[1])[1]
        tile_e = max(coordinates, key=lambda x: x[0])[0]
        tile_w = min(coordinates, key=lambda x: x[0])[0]

        depths = depth_map_service.get_within_box(tile_n, tile_s, tile_e, tile_w)

        if len(depths) == 0:
            continue

        img = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        for depth in depths:
            coordinates = depth["geom"]["coordinates"][0]
            grid_n = max(coordinates, key=lambda x: x[1])[1]
            grid_s = min(coordinates, key=lambda x: x[1])[1]
            grid_e = max(coordinates, key=lambda x: x[0])[0]
            grid_w = min(coordinates, key=lambda x: x[0])[0]

            # remove offset
            # n-s is reversed, as increase in pixel, is moving down,
            # while increase in latitude is moving up.
            grid_g_n = map(grid_n, tile_s, tile_n, 255, 0)
            grid_g_s = map(grid_s, tile_s, tile_n, 255, 0)
            grid_g_e = map(grid_e, tile_w, tile_e, 0, 255)
            grid_g_w = map(grid_w, tile_w, tile_e, 0, 255)

            min_depth = depth["depth"]
            min_depth_color = int(map(min_depth, 0, max_depth, 0, 255))
            color = (min_depth_color, 0, 255 - min_depth_color)

            draw.rectangle([(grid_g_w, grid_g_s), (grid_g_e, grid_g_n)], fill=color)

            # debug
            draw.text(
                (128, 128), f"{tile['z']}-{tile['x']}-{tile['y']}", fill=(0, 0, 0)
            )

        img.save(f"ais_app/tiles/{tile['z']}-{tile['x']}-{tile['y']}.png")

    return "Server go brbrbr"
