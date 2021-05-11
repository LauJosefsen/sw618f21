import math

from dependency_injector.wiring import inject, Provide
from flask import Blueprint, send_file
from PIL import Image, ImageDraw
from scipy.interpolate import interp1d
from math import pi, log, tan

from ais_app.containers import Container
from ais_app.services.depth_map_service import DepthMapService
from ais_app.services.enc_cell_service import EncCellService

blueprint = Blueprint("depth_map", __name__)


@blueprint.route("/tile/<z>/<x>/<y>")
def get_tile(z, x, y):
    try:
        response = send_file(f"tiles/{z}-{x}-{y}.png", mimetype='image/png')
    except FileNotFoundError:
        response = send_file("blank.png", mimetype="image/png")
    return response


def map(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


def coords_to_mercator_pixel(tuple, map_size):
    latitude = tuple[0]
    longitude = tuple[1]

    map_width = map_size
    map_height = map_size

    x = (longitude + 180) * (map_width / 360)
    latRad = latitude * pi / 180
    mercN = log(tan((pi / 4) + (latRad / 2)))
    y = (map_height / 2) - (map_width * mercN / (2 * pi))
    return x, y


def mercator_pixel_to_coords(tuple, map_size):
    x = tuple[0]
    y = tuple[1]

    long = (360 * x) / map_size - 180

    lat = 90 * (((4 * math.atan(
        math.e ** ((math.pi * (map_size - 2 * y)) / map_size))) / math.pi) + 3)

    return lat, long


@blueprint.route("/generate")
@inject
def generate_depth_map(
        enc_cell_service: EncCellService = Provide[Container.enc_cell_service],
        depth_map_service: DepthMapService = Provide[Container.depth_map_service],
):
    largest_enc = enc_cell_service.get_largest()
    enc_coordinates = largest_enc['location']['coordinates'][0]

    min_lat_enc = min(enc_coordinates, key=lambda x: x[1])[1]
    min_long_enc = min(enc_coordinates, key=lambda x: x[0])[0]

    max_lat_enc = max(enc_coordinates, key=lambda x: x[1])[1]
    max_long_enc = max(enc_coordinates, key=lambda x: x[0])[0]

    for z in range(7, 9):  # todo change back to 13
        print(f"Generation z-layer {z}")
        grid_size_long = 360 / (2 ** z)
        grid_size_lat = 180 / (2 ** z)

        grid_start_long = math.floor(
            (min_long_enc + 180) / grid_size_long
        )

        grid_end_long = math.ceil(
            (max_long_enc + 180) / grid_size_long
        )

        grid_start_lat = math.floor(
            (min_lat_enc) / grid_size_lat
        )

        grid_end_lat = math.ceil(
            (max_lat_enc) / grid_size_lat
        )

        for x in range(grid_start_long, grid_end_long):
            for y in range(grid_start_lat, grid_end_lat):
                # generate png in 256x256
                w = x * grid_size_long - 180
                e = (x + 1) * grid_size_long - 180
                n = y * grid_size_lat
                s = (y + 1) * grid_size_lat

                depth_map_data = depth_map_service.get_within_box(n, s, e, w)

                ns_mapper = interp1d([n, s], [0, 255], bounds_error=False, fill_value="extrapolate")
                ew_mapper = interp1d([e, w], [0, 255], bounds_error=False, fill_value="extrapolate")

                img = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
                draw = ImageDraw.Draw(img)
                for depth_data in depth_map_data:
                    coordinates = depth_data['geom']['coordinates'][0]
                    cell_s = map(min(coordinates, key=lambda x: x[1])[1], s, n, 255, 0)
                    cell_w = map(min(coordinates, key=lambda x: x[0])[0], w, e, 0, 255)
                    cell_n = map(max(coordinates, key=lambda x: x[1])[1], s, n, 255, 0)
                    cell_e = map(max(coordinates, key=lambda x: x[0])[0], w, e, 0, 255)
                    draw.rectangle([(cell_s, cell_w), (cell_n, cell_e)], fill="#ffff33ff",
                                   outline="red")
                    draw.text((128, 128), f"{z}-{x}-{y}", fill=(0, 0, 0))

                img.save(f"ais_app/tiles/{z}-{x}-{y}.png")
    return "Server go brbrbr"
