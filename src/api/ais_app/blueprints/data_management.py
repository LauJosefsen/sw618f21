from dependency_injector.wiring import inject, Provide
from flask import Blueprint, jsonify

from ais_app.containers import Container
from ais_app.services.import_ais_service import ImportAisService
from ais_app.services.space_data_preprocessing_service import (
    SpaceDataPreprocessingService,
)

blueprint = Blueprint("data_management", __name__)

"""
@api {get} /data_management/import
@apiGroup Data management
@apiDescription Imports all CSV files in the import directory into the connected database.

@apiSuccess {bool} success True if succeeded
"""


@blueprint.route("/import")
@inject
def import_ais_data(
    import_ais_service: ImportAisService = Provide[Container.import_ais_service],
):
    import_ais_service.import_ais_data()
    return jsonify({"success": True})


"""
@api {get} /data_management/cluster
@apiGroup Data management
@apiDescription Runs the clustering algorithm on the input data, and splits it into ships, tracks and points.

@apiSuccess {bool} success True if succeeded
"""


@blueprint.route("/cluster")
@inject
def cluster_points(
    space_data_preprocessing_service: SpaceDataPreprocessingService = Provide[
        Container.space_data_preprocessing_service
    ],
):
    space_data_preprocessing_service.cluster_points()
    return jsonify({"success": True})
