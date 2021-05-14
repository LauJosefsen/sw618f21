import json

from ais_app.helpers import build_dict
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
