import os

from ais_app.repository.enc_cell_repository import EncCellRepository


class EncCellService:
    __enc_cell_repository = EncCellRepository()

    def get_enc_cells_within_area_bounds_and_search(self, area_limits=None, search=""):
        if area_limits is None:
            area_limits = []

        enc_cells = self.__enc_cell_repository.get_enc_cells_search(search)

        filtered_enc_cells = []
        for enc in enc_cells:
            for limit in area_limits:
                if limit[0] < int(enc["area"]) < limit[1]:
                    filtered_enc_cells.append(enc)

        return filtered_enc_cells

    def import_enc_cell_files(self):
        print("Importing enc data..")
        for entry in os.scandir("./import"):
            if not entry.is_dir() and ".txt" in entry.name:
                print(f"Importing {entry.name}")
                self.__enc_cell_repository.import_enc_file(entry.path)
                print(f"Done importing {entry.name}")
