import json
import pandas as pd

from ais_app.helpers import build_dict, MinMaxXy
from ais_app.repository.sql_connector import SqlConnector


class GridRepository:
    __sql_connector = SqlConnector()

    def get_intervals(self, group_size):
        connection = self.__sql_connector.get_db_connection()
        cursor = connection.cursor()

        query = """
        with min_max AS (SELECT min(i) as min_i, min(j) as min_j, max(i) as max_i, max(j) as max_j FROM grid)
        SELECT
            *
            FROM 
                generate_series(
                    (SELECT min_max.min_i FROM min_max),
                    (SELECT min_max.max_i FROM min_max),
                %s) AS i,
                generate_series(
                    (SELECT min_max.min_j FROM min_max),
                     (SELECT min_max.max_j FROM min_max),
                %s) AS j
        """

        cursor.execute(query, (group_size, group_size))

        groups = [build_dict(cursor, row) for row in cursor.fetchall()]
        connection.close()

        return groups
