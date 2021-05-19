import json

from tqdm import tqdm
import numpy as np

from ais_app.helpers import build_dict, MinMaxXy
from ais_app.repository.sql_connector import SqlConnector


class DepthMapRepository:
    __sql_connector = SqlConnector()

    def get_within_box(self, n, s, e, w):
        connection = self.__sql_connector.get_db_connection()
        cursor = connection.cursor()

        # Use 3857 here instead of 25832, as this is used to draw tiles on leaflet directly.
        query = """
                SELECT
                    ST_AsGeoJson(ST_Transform(grid.geom, 3857)) as geom,
                    max_draught_map.min_depth as depth
                FROM max_draught_map
                JOIN grid ON grid.i = max_draught_map.i AND grid.j = max_draught_map.j
                WHERE ST_Intersects(
                    ST_Transform(ST_SetSRID(ST_MakePolygon(ST_GeomFromText(
                        'LINESTRING(%s %s,%s %s,%s %s, %s %s, %s %s)'
                        )), 3857),4326),
                    grid.geom
                )
                """

        cursor.execute(query, (w, n, e, n, e, s, w, s, w, n))
        depths = [build_dict(cursor, row) for row in cursor.fetchall()]

        for depth in depths:
            depth["geom"] = json.loads(depth["geom"])

        return depths

    def get_map_tiles(self, min_zoom: int, max_zoom: int):
        connection = self.__sql_connector.get_db_connection()
        cursor = connection.cursor()

        query = "SELECT z,x,y, ST_AsGeoJson(geom) as geom FROM get_tile_grids(%s,%s)"

        cursor.execute(query, (min_zoom, max_zoom))
        tiles = [build_dict(cursor, row) for row in cursor.fetchall()]

        for tile in tiles:
            tile["geom"] = json.loads(tile["geom"])

        return tiles

    def get_max_depth(self):
        connection = self.__sql_connector.get_db_connection()
        cursor = connection.cursor()

        query = "SELECT max(min_depth) as max FROM max_draught_map"

        cursor.execute(query)
        max = cursor.fetchone()

        return max[0]

    def get_max_depth_interpolated(self):
        connection = self.__sql_connector.get_db_connection()
        cursor = connection.cursor()

        query = "SELECT max(depth) as max FROM depth_map_interpolated"

        cursor.execute(query)
        max = cursor.fetchone()

        return max[0]

    def get_min_depth_as_points_in_enc_in_utm32n(self, enc_id):
        conn = self.__sql_connector.get_db_connection()
        cursor = conn.cursor()

        query = """
                with draught_map as (
                SELECT min_depth, st_centroid(st_transform(g.geom, 25832)) as geom FROM max_draught_map
                JOIN grid g on max_draught_map.i = g.i and max_draught_map.j = g.j
                JOIN enc_cell_with_utm32n enc_cell ON st_intersects(enc_cell.utm32n_geom, st_transform(g.geom, 25832))
                WHERE enc_cell.cell_id = %s
                )
                SELECT ST_X(geom) as x, ST_y(geom) as y, min_depth as z FROM draught_map
                """
        cursor.execute(query, (enc_id,))

        return [build_dict(cursor, row) for row in cursor.fetchall()]

    def truncate_interpolated_depth_map(self):
        conn = self.__sql_connector.get_db_connection()
        cursor = conn.cursor()

        query = """TRUNCATE TABLE interpolated_depth;"""
        cursor.execute(query)
        conn.commit()
        conn.close()

    def insert_interpolated_depths(self, depths, varians, bounds, grid_size):
        conn = self.__sql_connector.get_db_connection()
        cursor = conn.cursor()

        for iy, ix in tqdm(np.ndindex(depths.shape)):
            abs_bounds = MinMaxXy(
                bounds.min_x + grid_size * ix,
                bounds.min_y + grid_size * iy,
                bounds.min_x + grid_size * (ix + 1),
                bounds.min_y + grid_size * (iy + 1),
            )
            query = """
                        INSERT INTO interpolated_depth
                        SELECT i, j, %s, %s FROM grid
                        WHERE ST_Contains(grid.geom, st_transform(ST_SetSrid(st_makepoint(%s, %s), 25832), 4326));
                    """
            cursor.execute(
                query,
                (
                    depths[iy][ix],
                    varians[iy][ix],
                    (abs_bounds.max_x + abs_bounds.min_x) / 2,
                    (abs_bounds.max_y + abs_bounds.min_y) / 2,
                ),
            )

        conn.commit()
        conn.close()

    def get_within_box_interpolated(self, tile_bounds):
        connection = self.__sql_connector.get_db_connection()
        cursor = connection.cursor()

        # Use 3857 here instead of 25832, as this is used to draw tiles on leaflet directly.
        query = """
                        SELECT
                            ST_AsGeoJson(ST_Transform(grid.geom, 3857)) as geom,
                            depth,
                            varians
                        FROM interpolated_depth
                        JOIN grid ON grid.i = interpolated_depth.i AND grid.j = interpolated_depth.j
                        WHERE ST_Intersects(
                            ST_Transform(ST_SetSRID(ST_MakeBox2D(
                                ST_Point(%s, %s),
	                            ST_Point(%s ,%s)
	                        ), 3857),4326),
                            grid.geom
                        )
                        """

        cursor.execute(
            query,
            (
                tile_bounds.min_x,
                tile_bounds.min_y,
                tile_bounds.max_x,
                tile_bounds.max_y,
            ),
        )
        depths = [build_dict(cursor, row) for row in cursor.fetchall()]

        for depth in depths:
            depth["geom"] = json.loads(depth["geom"])

        return depths

    def generate_raw_depth_map(self):
        connection = self.__sql_connector.get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM generate_depth_map()")
        connection.commit()
        connection.close()
