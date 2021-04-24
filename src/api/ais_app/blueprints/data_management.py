from dependency_injector.wiring import inject, Provide
from flask import Blueprint

from ais_app.containers import Container
from ais_app.services.import_ais_service import ImportAisService
from ais_app.services.space_data_preprocessing_service import (
    SpaceDataPreprocessingService,
)

blueprint = Blueprint("data_management", __name__)


@blueprint.route("/import")
@inject
def import_ais_data(
    import_ais_service: ImportAisService = Provide[Container.import_ais_service],
):
    import_ais_service.import_ais_data()
    return "Ok"


@blueprint.route("/cluster")
@inject
def cluster_points(
    space_data_preprocessing_service: SpaceDataPreprocessingService = Provide[
        Container.space_data_preprocessing_service
    ],
):
    space_data_preprocessing_service.cluster_points()
    return "Ok"
