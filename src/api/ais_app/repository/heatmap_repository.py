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
                        SELECT grid.geom, intensity AS intensity
                        FROM heatmap_point_density as heatmap
                        JOIN grid ON grid.i = heatmap.i AND grid.j  = heatmap.j
                        JOIN enc_cells as enc on st_contains(enc.location, grid.geom)
                        WHERE
                            enc.cell_id = %s AND
                            heatmap.intensity > 0 AND
                            heatmap.ship_type = ANY (string_to_array(%s, ','))
                    ),
                    max_intensity AS 
                    (SELECT MAX(intensity) as max FROM heatmap_data)
                    SELECT
                        ST_AsGeoJson(ST_FlipCoordinates(ST_Centroid(geom))) as grid_point,
                        (intensity * 100)/(SELECT max FROM max_intensity) as intensity
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
                    SELECT grid.geom, intensity
                    FROM heatmap_trafic_density as heatmap
                    JOIN grid_2k grid ON grid.i = heatmap.i AND grid.j  = heatmap.j
                    JOIN enc_cells as enc on st_contains(enc.location, grid.geom)
                    WHERE
                        enc.cell_id = %s AND
                        heatmap.intensity > 0 AND
                        heatmap.ship_type = ANY (string_to_array(%s, ','))
                ),
                max_intensity AS 
                    (SELECT MAX(intensity) as max FROM heatmap_data)
                SELECT
                    ST_AsGeoJson(ST_FlipCoordinates(ST_Centroid(geom))) as grid_point,
                    (intensity * 100)/(SELECT max FROM max_intensity) as intensity
                FROM heatmap_data
            """
        cursor.execute(query, (enc_cell_id, ",".join(ship_types)))

        points = [build_dict(cursor, row) for row in cursor.fetchall()]

        connection.close()

        for point in points:
            point["grid_point"] = json.loads(point["grid_point"])

        return points


    def get_time_interval_in_hours(self):
        connection = self.__sql_connector.get_db_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT EXTRACT(epoch FROM max(timestamp)-min(timestamp))/3600 as interval FROM points
        """)

        hours = cursor.fetchone()[0]

        connection.close()

        return hours

    def truncate_point_density(self):
        connection = self.__sql_connector.get_db_connection()
        cursor = connection.cursor()

        cursor.execute("TRUNCATE TABLE heatmap_point_density")

        connection.commit()

        connection.close()

    @staticmethod
    def apply_point_density_generate(task, shared_info, conn):
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO heatmap_point_density
            SELECT g.i, g.j, s.ship_type, 
                (
                    COUNT(p) FILTER (WHERE s.mobile_type = 'Class B') * 3 +
                    COUNT(p) FILTER (WHERE s.mobile_type = 'Class A')
                )/(ST_Area(g.geom, true) * %s)
            FROM grid g
            JOIN points p ON ST_Contains(g.geom, p.location)
            JOIN track t on p.track_id = t.id
            JOIN ship s on t.ship_id = s.id
            WHERE  g.i >= %s AND g.i < %s + 100 AND g.j >= %s AND g.j < %s + 100 
            AND p.sog > 2 AND p.sog < 4.4
            GROUP BY g.i, g.j, s.ship_type, g.geom
            HAVING (
                    COUNT(p) FILTER (WHERE s.mobile_type = 'Class B') * 3 +
                    COUNT(p) FILTER (WHERE s.mobile_type = 'Class A')
                )/(ST_Area(g.geom, true) * %s) IS NOT null
        """,
            (
                shared_info,
                task["i"],
                task["i"],
                task["j"],
                task["j"],
                shared_info
            ),
        )

    @staticmethod
    def apply_trafic_density_generate(task, shared_info, conn):
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO heatmap_trafic_density
            SELECT g.i, g.j, s.ship_type, 
                SUM(ST_NumGeometries(ST_ClipByBox2d(t.geom, g.geom)))
                /(ST_Area(g.geom, true) * %s)
            FROM grid_2k g, track_with_geom t
            JOIN ship s on t.ship_id = s.id
            WHERE  g.i >= %s AND g.i < %s + 10 AND g.j >= %s AND g.j < %s + 10
            GROUP BY g.i, g.j, s.ship_type, g.geom
            HAVING SUM(ST_NumGeometries(ST_ClipByBox2d(t.geom, g.geom)))
                /(ST_Area(g.geom, true) * %s) != 0
        """,
            (
                shared_info,
                task["i"],
                task["i"],
                task["j"],
                task["j"],
                shared_info
            ),
        )

    def truncate_trafic_density(self):
        connection = self.__sql_connector.get_db_connection()
        cursor = connection.cursor()

        cursor.execute("TRUNCATE TABLE heatmap_trafic_density")

        connection.commit()

        connection.close()
