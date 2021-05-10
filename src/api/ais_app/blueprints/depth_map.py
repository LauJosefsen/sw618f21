import math

from dependency_injector.wiring import inject, Provide
from flask import Blueprint, send_file
from PIL import Image, ImageDraw
from scipy.interpolate import interp1d

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

    for z in range(7, 9): #todo change back to 13
        print(f"Generation z-layer {z}")
        grid_size_long = 360 / (2 ** z)
        grid_size_lat = 180 / (2 ** z)

        grid_start_long = math.floor(
            (min_long_enc+180) / grid_size_long
        )

        grid_end_long = math.ceil(
            (max_long_enc+180) / grid_size_long
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

                ns_mapper = interp1d([n, s], [0, 255], bounds_error=False)
                ew_mapper = interp1d([e, w], [0, 255], bounds_error=False)

                img = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
                draw = ImageDraw.Draw(img)
                for depth_data in depth_map_data:
                    coordinates = depth_data['geom']['coordinates'][0]
                    cell_s = ns_mapper(min(coordinates, key=lambda x: x[1])[1])
                    cell_w = ew_mapper(min(coordinates, key=lambda x: x[0])[0])
                    cell_n = ns_mapper(max(coordinates, key=lambda x: x[1])[1])
                    cell_e = ew_mapper(max(coordinates, key=lambda x: x[0])[0])
                    draw.rectangle([(cell_s,cell_w),(cell_n,cell_e)], fill ="#ffff33ff", outline ="red")


                img.save(f"ais_app/tiles/{z}-{x}-{y}.png")
    return "Server go brbrbr"
