import os

from ais_app.repository.depth_map_repository import DepthMapRepository
from ais_app.repository.enc_cell_repository import EncCellRepository


class DepthMapService:
    __depth_map_repository = DepthMapRepository()

    def get_within_box(self, n,s,e,w):
        return self.__depth_map_repository.get_within_box(n,s,e,w)


