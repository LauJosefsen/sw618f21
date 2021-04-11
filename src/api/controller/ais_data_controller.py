import json

import geopy
import shapely.geometry

from container import Container
from dependency_injector.wiring import Provide, inject
from flask import request

from data_management.make_grid import make_grid_mercator, make_grid_meters
from service.ais_data_service import AisDataService
from flask import jsonify


@inject
def index(ais_data_service: AisDataService = Provide[Container.ais_data_service]):
    return jsonify(ais_data_service.fetch_all_limit("data", 20, 0))


@inject
def import_ais_data(
        ais_data_service: AisDataService = Provide[Container.ais_data_service],
):
    ais_data_service.import_ais_data()
    return ""


@inject
def cluster_points(
        ais_data_service: AisDataService = Provide[Container.ais_data_service],
):
    data = ais_data_service.cluster_points()
    return jsonify(data)


@inject
def get_tracks(ais_data_service: AisDataService = Provide[Container.ais_data_service]):
    limit = request.args.get("limit", default=1, type=int)
    offset = request.args.get("offset", default=0, type=int)
    simplify = request.args.get("simplify", default=0, type=int)
    mmsi = request.args.get("search", default=None, type=int)
    return jsonify(
        ais_data_service.get_tracks(
            limit, offset, simplify_tolerance=simplify, search_mmsi=mmsi
        )
    )


@inject
def import_enc_data(
        ais_data_service: AisDataService = Provide[Container.ais_data_service],
):
    ais_data_service.import_enc_data()
    return "done"


@inject
def get_enc_cells(
        ais_data_service: AisDataService = Provide[Container.ais_data_service],
):
    limit = request.args.get("limit", default=1, type=int)
    offset = request.args.get("offset", default=0, type=int)

    objs = ais_data_service.fetch_specific_limit(
        "cell_name, cell_title," " ST_AsGeoJson(public.enc_cells.location) as location",
        "enc_cells",
        limit,
        offset,
    )
    for obj in objs:
        obj["location"] = json.loads(obj["location"])
    return jsonify(objs)


# TODO This is WIP and we are currently testing on pgadmin
@inject
def cluster_heatmap(
        ais_data_service: AisDataService = Provide[Container.ais_data_service],
):
    # grid = make_grid_mercator(geopy.Point((56, 10)), geopy.Point((57, 11)), 100)
    # grid = make_grid_meters(geopy.Point((56, 10)), geopy.Point((57, 11)), 10000)
    # grid = make_grid_meters(geopy.Point((70, 10)), geopy.Point((80, 20)), 10000)
    grid = make_grid_mercator(geopy.Point((70, 10)), geopy.Point((80, 20)), 100)

    # for index, rect in enumerate(grid):
    #     grid[index]['coordinates'] = list(grid[index]['coordinates'])
    #     grid[index]['coordinates'][0] = list(grid[index]['coordinates'][0])
    #     for index2, coord in enumerate(rect['coordinates'][0]):
    #         grid[index]['coordinates'][0][index2] = (coord[1], coord[0])

    return jsonify(grid)

    # return jsonify(make_grid(
    #     geopy.Point((59, -50)), geopy.Point((80, 0)), 1, in_meters=False
    # )
    # )
    # objs = ais_data_service.make_heatmap(0.05, 50)
