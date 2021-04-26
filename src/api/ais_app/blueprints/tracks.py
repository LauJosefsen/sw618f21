from dependency_injector.wiring import inject, Provide
from flask import Blueprint, request, jsonify

from ais_app.containers import Container
from ais_app.services.track_service import TrackService

blueprint = Blueprint("tracks", __name__)


@blueprint.route("/get_by_enc_id")
@inject
def get_by_enc_id(
    track_service: TrackService = Provide[Container.track_service],
):
    enc_cell_id = request.args.get("enc_cell_id", default=1, type=int)
    return jsonify(track_service.get_tracks_in_enc(enc_cell_id))
