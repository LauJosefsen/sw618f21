"""Containers module."""

from dependency_injector import containers, providers

from ais_app.services.ais_data_service import AisDataService
from ais_app.services.enc_cell_service import EncCellService
from ais_app.services.heatmap_service import HeatmapService
from ais_app.services.import_ais_service import ImportAisService
from ais_app.services.space_data_preprocessing_service import (
    SpaceDataPreprocessingService,
)
from ais_app.services.track_service import TrackService


class Container(containers.DeclarativeContainer):
    ais_data_service = providers.Factory(AisDataService)
    enc_cell_service = providers.Factory(EncCellService)
    heatmap_service = providers.Factory(HeatmapService)
    import_ais_service = providers.Factory(ImportAisService)
    space_data_preprocessing_service = providers.Factory(SpaceDataPreprocessingService)
    track_service = providers.Factory(TrackService)
