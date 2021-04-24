"""Containers module."""

from dependency_injector import containers, providers

from ais_app.services.ais_data_service import AisDataService


class Container(containers.DeclarativeContainer):
    ais_data_service = providers.Factory(AisDataService)
