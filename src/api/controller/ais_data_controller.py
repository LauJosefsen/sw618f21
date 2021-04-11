import json
import shapely.geometry
from container import Container
from dependency_injector.wiring import Provide, inject
from flask import request
from data_management.make_grid import make_grid
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
    return jsonify(
        {
            "coordinates": make_grid(
                shapely.geometry.Point((9, 55)), shapely.geometry.Point((12, 58)), 50000
            )
        }
    )
    # objs = ais_data_service.make_heatmap(0.05, 50)

@inject
def find_ais_time_median(
    ais_data_service: AisDataService = Provide[Container.ais_data_service],
):
    return jsonify(ais_data_service.find_ais_time_median())