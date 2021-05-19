import json

from ais_app.helpers import build_dict
from ais_app.repository.sql_connector import SqlConnector


class HeatmapRepository:
    __sql_connector = SqlConnector()

    def get_point_density_heatmap_for_enc(
        self, enc_cell_id, ship_types: list[str] = None
    ):
        if ship_types is None:
            ship_types = []

        connection = self.__sql_connector.get_db_connection()
        cursor = connection.cursor()
        query = """
                    WITH heatmap_data AS (
                        SELECT grid.geom, SUM(intensity) AS intensity
                        FROM heatmap_point_density as heatmap
                        JOIN grid ON grid.i = heatmap.i AND grid.j  = heatmap.j
                        JOIN enc_cells as enc on st_contains(enc.location, grid.geom)
                        WHERE
                            enc.cell_id = %s AND
                            heatmap.intensity > 0 AND
                            heatmap.ship_type = ANY (string_to_array(%s, ','))
                        GROUP BY grid.geom
                    )
                    SELECT
                        ST_AsGeoJson(ST_FlipCoordinates(ST_Centroid(geom))) as grid_point,
                        intensity * 100 as intensity
                    FROM heatmap_data
                    """
        cursor.execute(query, (enc_cell_id, ",".join(ship_types)))

        points = [build_dict(cursor, row) for row in cursor.fetchall()]

        connection.close()

        for point in points:
            point["grid_point"] = json.loads(point["grid_point"])

        return points

    def get_trafic_density_heatmap_for_enc(self, enc_cell_id, ship_types: list[str]):
        connection = self.__sql_connector.get_db_connection()
        cursor = connection.cursor()
        query = """
                WITH heatmap_data AS (
                    SELECT grid.geom, SUM(intensity) AS intensity
                    FROM heatmap_trafic_density as heatmap
                    JOIN grid ON grid.i = heatmap.i AND grid.j  = heatmap.j
                    JOIN enc_cells as enc on st_contains(enc.location, grid.geom)
                    WHERE
                        enc.cell_id = %s AND
                        heatmap.intensity > 0 AND
                        heatmap.ship_type = ANY (string_to_array(%s, ','))
                    GROUP BY grid.geom
                )
                SELECT
                    ST_AsGeoJson(ST_FlipCoordinates(ST_Centroid(geom))) as grid_point,
                    intensity * 100 as intensity
                FROM heatmap_data
            """
        cursor.execute(query, (enc_cell_id, ",".join(ship_types)))

        points = [build_dict(cursor, row) for row in cursor.fetchall()]

        connection.close()

        for point in points:
            point["grid_point"] = json.loads(point["grid_point"])

        return points

    def generate_traffic_density_heatmap(self):
        connection = self.__sql_connector.get_db_connection()

        connection.cursor().execute("SELECT * FROM generate_trafic_density_heatmap();")

        connection.close()

    def generate_point_density_heatmap(self):
        connection = self.__sql_connector.get_db_connection()

        connection.cursor().execute("SELECT * FROM generate_point_density_heatmap();")

        connection.close()
