from dependency_injector import containers, providers
from service.ais_data_service import AisDataService


class Container(containers.DeclarativeContainer):
    ais_data_service = providers.Factory(AisDataService,)
