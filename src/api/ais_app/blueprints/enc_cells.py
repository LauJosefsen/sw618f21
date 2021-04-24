from dependency_injector.wiring import inject, Provide
from flask import Blueprint, request, jsonify

from ais_app.containers import Container
from ais_app.services.ais_data_service import AisDataService

blueprint = Blueprint("enc_cells", __name__)


@blueprint.route("/import")
@inject
def import_enc_data(
    ais_data_service: AisDataService = Provide[Container.ais_data_service],
):
    ais_data_service.import_enc_data()
    return "done"


@blueprint.route("/get_by_area_bounds")
@inject
def get_by_size_bounds(
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
