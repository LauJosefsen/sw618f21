from ais_app.repository.enc_cell_repository import EncCellRepository
from ais_app.repository.track_repository import TrackRepository


class TrackService:
    __track_repository = TrackRepository()
    __enc_repository = EncCellRepository()

    def get_tracks(self, limit, offset, simplify_tolerance=0, search_mmsi=None):
        return self.__track_repository.get_tracks_limit_offset_search_mmsi_simplify(
            limit, offset, simplify_tolerance, search_mmsi
        )

    def get_tracks_in_enc(self, enc_cell_id: int):
        tracks = self.__track_repository.get_tracks_in_enc_cell(
            enc_cell_id
        )

        enc_cell = self.__enc_repository.get_enc_cells_by_id(enc_cell_id)

        return {"tracks": tracks, "enc": enc_cell}
