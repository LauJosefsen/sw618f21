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
    data = ais_data_service.new_cluster()
    return jsonify(data)


@inject
def get_routes(ais_data_service: AisDataService = Provide[Container.ais_data_service]):
    limit = request.args.get("limit", default=1, type=int)
    offset = request.args.get("offset", default=0, type=int)
    simplify = request.args.get("simplify", default=0, type=int)
    return jsonify(
        ais_data_service.get_routes(limit, offset, simplify_tolerance=simplify)
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
    return jsonify(
        ais_data_service.fetch_specific_limit(
            "cell_name, cell_title, edition, edition_date, update, update_date, ST_AsText(public.enc_cells.location) as location",
            "enc_cells",
            limit,
            offset,
        )
    )
