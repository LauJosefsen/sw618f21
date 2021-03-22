from container import Container
from dependency_injector.wiring import Provide, inject
from flask import request
from service.ais_data_service import AisDataService
from flask import jsonify


@inject
def index(ais_data_service: AisDataService = Provide[Container.ais_data_service]):
    return jsonify(ais_data_service.fetch_limit(20, 0))


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
    data = ais_data_service.new_cluster()
    return jsonify(data)


@inject
def get_routes(ais_data_service: AisDataService = Provide[Container.ais_data_service]):
    limit = request.args.get("limit", default=1, type=int)
    offset = request.args.get("offset", default=0, type=int)
    return jsonify(ais_data_service.get_routes(100000, 1))
