from ais_app.repository.enc_cell_repository import EncCellRepository
from ais_app.repository.heatmap_repository import HeatmapRepository


class HeatmapService:
    __heatmap_repository = HeatmapRepository()
    __enc_cell_repository = EncCellRepository()

    def simple_heatmap(self, enc_cell_id: int):
        points = self.__heatmap_repository.get_simple_heatmap_for_enc(enc_cell_id)

        enc_cell = self.__enc_cell_repository.get_enc_cells_by_id(enc_cell_id)

        points_formatted = self.__format_to_leaflet_heatlayer(points)

        return {"enc": enc_cell, "heatmap_data": points_formatted}

    def trafic_density_heatmap(self, enc_cell_id: int):
        points = self.__heatmap_repository.get_trafic_density_heatmap_for_enc(
            enc_cell_id
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

    def generate_trafic_density(self):
        self.__heatmap_repository.generate_trafic_density_heatmap()
