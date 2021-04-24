from dependency_injector.wiring import inject, Provide
from flask import Blueprint, request, jsonify

from ais_app.containers import Container
from ais_app.services.ais_data_service import AisDataService

blueprint = Blueprint("heatmaps", __name__)


@blueprint.route("/simple")
@inject
def simple_heatmap(
    ais_data_service: AisDataService = Provide[Container.ais_data_service],
):
    enc_cell_id = request.args.get("enc_cell_id", default=0, type=int)
    return jsonify(ais_data_service.simple_heatmap(enc_cell_id))


@blueprint.route("/trafic_density")
@inject
def trafic_density_heatmap(
    ais_data_service: AisDataService = Provide[Container.ais_data_service],
):
    enc_cell_id = request.args.get("enc_cell_id", default=0, type=int)
    return jsonify(ais_data_service.trafic_density_heatmap(enc_cell_id))
