from psycopg2.extensions import AsIs

from ais_app.helpers import build_dict
from ais_app.repository.sql_connector import SqlConnector


class AbstractRepository:
    sql_connector = SqlConnector()

    def fetch_all_limit(self, table_name, limit, offset=0):
        connection = self.sql_connector.get_db_connection()
        cursor = connection.cursor()
        query = "SELECT * FROM public.%s LIMIT %s OFFSET %s;"

        # todo: This is bad practice, we should avoid having table name as a parameter.
        cursor.execute(query, (AsIs(table_name), limit, offset))

        data = [build_dict(cursor, row) for row in cursor.fetchall()]

        connection.close()

        return data

    def fetch_specific_limit(self, col_names, table_name, limit, offset):
        connection = self.sql_connector.get_db_connection()
        cursor = connection.cursor()
        query = "SELECT %s FROM public.%s LIMIT %s OFFSET %s;"

        # todo: This is bad practice, we should avoid having table name as a parameter.
        cursor.execute(query, (AsIs(col_names), AsIs(table_name), limit, offset))

        data = [build_dict(cursor, row) for row in cursor.fetchall()]

        connection.close()

        return data
