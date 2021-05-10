import json
import pandas as pd

from ais_app.helpers import build_dict
from ais_app.repository.sql_connector import SqlConnector


class DepthMapRepository:
    __sql_connector = SqlConnector()

    def get_within_box(self, n, s, e, w):
        connection = self.__sql_connector.get_db_connection()
        cursor = connection.cursor()

        query = """
                SELECT 
                    ST_AsGeoJson(grid.geom) as geom,
                    max_draught_map.min_depth as depth
                FROM max_draught_map 
                JOIN grid ON grid.i = max_draught_map.i AND grid.j = max_draught_map.j
                WHERE ST_Intersects(
                    ST_SetSRID(ST_MakePolygon(ST_GeomFromText(
                        'LINESTRING(%s %s,%s %s,%s %s, %s %s, %s %s)'
                        )), 4326),
                    grid.geom)
                
                """

        cursor.execute(query, (w, n, e, n, e, s, w, s, w, n))
        depths = [build_dict(cursor, row) for row in cursor.fetchall()]

        for depth in depths:
            depth["geom"] = json.loads(depth["geom"])

        return depths
