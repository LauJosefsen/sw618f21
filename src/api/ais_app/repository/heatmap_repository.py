import json

from ais_app.helpers import build_dict
from ais_app.repository.sql_connector import SqlConnector


class HeatmapRepository:
    __sql_connector = SqlConnector()

    def get_simple_heatmap_for_enc(self, enc_cell_id):
        connection = self.__sql_connector.get_db_connection()
        cursor = connection.cursor()
        query = """
                        WITH heatmap_data AS (
                            SELECT * FROM public.heatmap_10m as heatmap
                            JOIN enc_cells as enc on st_contains(enc.location, heatmap.grid_point)
                            WHERE enc.cell_id = %s
                        )
                        SELECT
                            ST_AsGeoJson(ST_FlipCoordinates(grid_point)) as grid_point,
                            (count*100.0/(SELECT MAX(count) FROM heatmap_data)) as intensity
                        FROM heatmap_data
                    """
        cursor.execute(query, (enc_cell_id,))

        connection.close()

        points = [build_dict(cursor, row) for row in cursor.fetchall()]

        for point in points:
            point["grid_point"] = json.loads(point["grid_point"])

        return points

    def get_trafic_density_heatmap_for_enc(self, enc_cell_id):
        connection = self.__sql_connector.get_db_connection()
        cursor = connection.cursor()
        query = """
                WITH heatmap_data AS (
                    SELECT geom, intensity FROM heatmap_trafic_density_1000m as heatmap
                    JOIN enc_cells as enc on st_contains(enc.location, heatmap.geom)
                    WHERE enc.cell_id = %s AND heatmap.intensity > 0
                )
                SELECT
                    ST_AsGeoJson(ST_FlipCoordinates(ST_Centroid(geom))) as grid_point,
                    (intensity*50000/(SELECT MAX(intensity) FROM heatmap_data)) as intensity
                FROM heatmap_data
            """
        cursor.execute(query, (enc_cell_id,))

        points = [build_dict(cursor, row) for row in cursor.fetchall()]

        connection.close()

        for point in points:
            point["grid_point"] = json.loads(point["grid_point"])

        return points
