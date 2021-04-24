from ais_app.repository.enc_cell_repository import EncCellRepository
from ais_app.repository.heatmap_repository import HeatmapRepository


class HeatmapService:
    __heatmap_repository = HeatmapRepository()
    __enc_cell_repository = EncCellRepository()

    def simple_heatmap(self, enc_cell_id: int):
        points = self.__heatmap_repository.get_simple_heatmap_for_enc(enc_cell_id)

        enc_cell = self.__enc_cell_repository.get_enc_cells_by_id(enc_cell_id)

        points_formatted = [
            [
                point["grid_point"]["coordinates"][0],
                point["grid_point"]["coordinates"][1],
                point["intensity"],
            ]
            for point in points
        ]

        return {"enc": enc_cell, "heatmap_data": points_formatted}

    def trafic_density_heatmap(self, enc_cell_id: int):
        points = self.__heatmap_repository.get_trafic_density_heatmap_for_enc(
            enc_cell_id
        )

        enc_cell = self.__enc_cell_repository.get_enc_cells_by_id(enc_cell_id)

        points_formatted = [
            [
                point["grid_point"]["coordinates"][0],
                point["grid_point"]["coordinates"][1],
                point["intensity"],
            ]
            for point in points
        ]

        return {"enc": enc_cell, "heatmap_data": points_formatted}
