from ais_app.repository.depth_map_repository import DepthMapRepository


class DepthMapService:
    __depth_map_repository = DepthMapRepository()

    def get_within_box(self, n, s, e, w):
        return self.__depth_map_repository.get_within_box(n, s, e, w)

    def get_map_tiles(self, min_zoom: int, max_zoom: int):
        return self.__depth_map_repository.get_map_tiles(min_zoom, max_zoom)

    def get_max_depth(self):
        return self.__depth_map_repository.get_max_depth()
