from dependency_injector.wiring import inject, Provide
from flask import Blueprint, request, jsonify

from ais_app.containers import Container
from ais_app.services.ais_data_service import AisDataService

blueprint = Blueprint("tracks", __name__)


@blueprint.route("/get_by_enc_id")
@inject
def get_by_enc_id(
    ais_data_service: AisDataService = Provide[Container.ais_data_service],
):
    enc_cell_id = request.args.get("enc_cell_id", default=1, type=int)
    simplify = request.args.get("simplify", default=0, type=int)
    return jsonify(
        ais_data_service.get_tracks_in_enc(enc_cell_id, simplify_tolerance=simplify)
    )
