from dependency_injector.wiring import inject, Provide
from flask import Blueprint, jsonify

from ais_app.containers import Container
from ais_app.services.ais_data_service import AisDataService

blueprint = Blueprint("data_management", __name__)


@blueprint.route("/import")
@inject
def import_ais_data(
    ais_data_service: AisDataService = Provide[Container.ais_data_service],
):
    ais_data_service.import_ais_data()
    return "Ok"


@blueprint.route("/cluster")
def cluster_points(
    ais_data_service: AisDataService = Provide[Container.ais_data_service],
):
    data = ais_data_service.cluster_points()
    return jsonify(data)


@blueprint.route("/find_time_median")
@inject
def find_ais_time_median(
    ais_data_service: AisDataService = Provide[Container.ais_data_service],
):
    return jsonify(ais_data_service.find_ais_time_median())
