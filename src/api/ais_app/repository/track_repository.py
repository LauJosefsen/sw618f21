import json

from ais_app.helpers import build_dict
from ais_app.repository.sql_connector import SqlConnector


class TrackRepository:
    __sql_connector = SqlConnector()

    def get_tracks_limit_offset_search_mmsi_simplify(
        self, limit: int, offset: int, search_mmsi: str, simplify: float
    ):
        connection = self.__sql_connector.get_db_connection()
        cursor = connection.cursor()

        query = """
                SELECT
                    t.id, t.mmsi AS mmsi, MIN(p.timestamp) AS timestamp_begin,
                    MAX(p.timestamp) AS timestamp_end,
                    ST_AsGeoJson(ST_FlipCoordinates(
                        ST_Simplify(ST_MakeLine(p.location ORDER BY p.timestamp), %s)
                        )) AS coordinates
                FROM public.track AS t
                JOIN public.points AS p ON t.id=p.track_id
                WHERE (%s OR t.mmsi = %s)
                GROUP BY t.id, t.mmsi
                LIMIT %s OFFSET %s;
                """

        cursor.execute(
            query,
            (
                simplify,
                True if search_mmsi is None else False,
                search_mmsi,
                limit,
                offset,
            ),
        )
        tracks = [build_dict(cursor, row) for row in cursor.fetchall()]

        connection.close()

        for row in tracks:
            row["coordinates"] = json.loads(row["coordinates"])["coordinates"]

        return tracks

    def get_tracks_in_enc_cell(self, enc_cell_id, ship_types: list[str]):
        connection = self.__sql_connector.get_db_connection()
        cursor = connection.cursor()

        query = """
            SELECT
                id, destination, cargo_type, eta, mmsi, imo, mobile_type, callsign, name, ship_type, width, length,
                draught, a, b, c, d, begin_ts, end_ts,
                ST_AsGeoJson(ST_FlipCoordinates(t.geom)) AS coordinates
            FROM public.track_with_geom AS t
            JOIN enc_cells AS enc ON ST_Intersects(enc.location, t.geom)
            WHERE 
                enc.cell_id = %s AND
                t.ship_type = ANY (string_to_array(%s, ','))
        """

        cursor.execute(
            query,
            (enc_cell_id, ",".join(ship_types)),
        )
        data = [build_dict(cursor, row) for row in cursor.fetchall()]

        connection.close()

        for row in data:
            row["coordinates"] = json.loads(row["coordinates"])["coordinates"]

        return data
