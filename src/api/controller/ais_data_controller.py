from container import Container
from dependency_injector.wiring import Provide, inject
from flask import request

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
    bounds = request.args.get("bounds", default="", type=str)
    bounds_parsed = [int(split) for split in bounds.split(",")]

    proper_bounds = []
    for idx, bound in enumerate(bounds_parsed):
        if idx % 2 == 0:
            proper_bounds.append([bounds_parsed[idx], bounds_parsed[idx + 1]])

    search = request.args.get("search", default="", type=str)

    return jsonify(
        ais_data_service.get_enc_cells(area_limits=proper_bounds, search=search)
    )


@inject
def cluster_heatmap(
    ais_data_service: AisDataService = Provide[Container.ais_data_service],
):
    enc_cell_id = request.args.get("enc_cell_id", default=0, type=int)
    return jsonify(ais_data_service.simple_heatmap(enc_cell_id))

@inject
def trafic_density_heatmap(
    ais_data_service: AisDataService = Provide[Container.ais_data_service],
):
    enc_cell_id = request.args.get("enc_cell_id", default=0, type=int)
    return jsonify(ais_data_service.trafic_density_heatmap(enc_cell_id))


@inject
def find_ais_time_median(
    ais_data_service: AisDataService = Provide[Container.ais_data_service],
):
    return jsonify(ais_data_service.find_ais_time_median())
