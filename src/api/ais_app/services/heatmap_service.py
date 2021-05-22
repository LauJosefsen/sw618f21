from ais_app.repository.enc_cell_repository import EncCellRepository
from ais_app.repository.heatmap_repository import HeatmapRepository
from ais_app.services.grid_service import GridService


class HeatmapService:
    __heatmap_repository = HeatmapRepository()
    __enc_cell_repository = EncCellRepository()

    def point_density_heatmap(self, enc_cell_id: int, ship_types: list[str] = None):
        if ship_types is None:
            ship_types = []

        points = self.__heatmap_repository.get_point_density_heatmap_for_enc(
            enc_cell_id, ship_types
        )

        enc_cell = self.__enc_cell_repository.get_enc_cells_by_id(enc_cell_id)

        points_formatted = self.__format_to_leaflet_heatlayer(points)

        return {"enc": enc_cell, "heatmap_data": points_formatted}

    def trafic_density_heatmap(self, enc_cell_id: int, ship_types: list[str]):
        points = self.__heatmap_repository.get_trafic_density_heatmap_for_enc(
            enc_cell_id, ship_types
        )

        enc_cell = self.__enc_cell_repository.get_enc_cells_by_id(enc_cell_id)

        points_formatted = self.__format_to_leaflet_heatlayer(points)

        return {"enc": enc_cell, "heatmap_data": points_formatted}

    @staticmethod
    def __format_to_leaflet_heatlayer(points):
        points_formatted = [
            [
                point["grid_point"]["coordinates"][0],
                point["grid_point"]["coordinates"][1],
                point["intensity"],
            ]
            for point in points
        ]
        return points_formatted

    def generate_traffic_density(self):
        hours = self.__heatmap_repository.get_time_interval_in_hours()
        self.__heatmap_repository.truncate_trafic_density()
        GridService().apply_to_grid_intervals(10, HeatmapRepository.apply_trafic_density_generate,
                                              shared_info=hours, grid_name="grid_2k")


    def generate_point_density(self):
        hours = self.__heatmap_repository.get_time_interval_in_hours()
        self.__heatmap_repository.truncate_point_density()
        GridService().apply_to_grid_intervals(100, HeatmapRepository.apply_point_density_generate, shared_info=hours)
