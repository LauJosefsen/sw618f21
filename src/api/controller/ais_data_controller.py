from container import Container
from dependency_injector.wiring import Provide, inject
from service.ais_data_service import AisDataService


@inject
def index(ais_data_service: AisDataService = Provide[Container.ais_data_service]):
    return {"data": ais_data_service.fetch_all()}