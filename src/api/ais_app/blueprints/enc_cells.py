from dependency_injector.wiring import inject, Provide
from flask import Blueprint, request, jsonify

from ais_app.containers import Container
from ais_app.services.enc_cell_service import EncCellService

blueprint = Blueprint("enc_cells", __name__)

"""
@api {get} /enc_cells/import
@apiGroup EncCells
@apiDescription Imports ENC_cells from txt files in import folder

@apiSuccess {bool} success True if succeeded
"""


@blueprint.route("/import")
@inject
def import_enc_data(
    enc_cell_service: EncCellService = Provide[Container.enc_cell_service],
):
    enc_cell_service.import_enc_cell_files()
    return "Ok"


"""
@api {get} /enc_cells/get_by_area_bounds
@apiGroup EncCells
@apiDescription Gets enc cells within some area bounds.

@apiParam {number[2][]} Pairs of area-bounds to filter for
@apiParam {string} search_string Free text filter

@apiSuccess {json} enc_cells The found enc_cells
"""


@blueprint.route("/get_by_area_bounds")
@inject
def get_by_size_bounds(
    enc_cell_service: EncCellService = Provide[Container.enc_cell_service],
):
    bounds = request.args.get("bounds", default="", type=str)
    bounds_parsed = [int(split) for split in bounds.split(",")]

    proper_bounds = []
    for idx, bound in enumerate(bounds_parsed):
        if idx % 2 == 0:
            proper_bounds.append([bounds_parsed[idx], bounds_parsed[idx + 1]])

    search = request.args.get("search", default="", type=str)

    return jsonify(
        enc_cell_service.get_enc_cells_within_area_bounds_and_search(
            area_limits=proper_bounds, search=search
        )
    )
