from dependency_injector.wiring import inject, Provide
from flask import Blueprint, request, jsonify

from ais_app.containers import Container
from ais_app.services.track_service import TrackService

blueprint = Blueprint("tracks", __name__)

"""
@api {get} /tracks/get_by_enc_id
@apiGroup Tracks
@apiDescription Get tracks in a given enc_cell

@apiParam {number} enc_id The enc to which to get the tracks for
@apiParam {string[]} ship_types The ship types to show

@apiSuccess {json} track_data The track data
"""


@blueprint.route("/get_by_enc_id")
@inject
def get_by_enc_id(
    track_service: TrackService = Provide[Container.track_service],
):
    enc_cell_id = request.args.get("enc_cell_id", default=1, type=int)
    ship_types = request.args.get("ship_types", default="", type=str).split(",")

    return jsonify(track_service.get_tracks_in_enc(enc_cell_id, ship_types))
