import json
import pandas as pd

from ais_app.helpers import build_dict
from ais_app.repository.sql_connector import SqlConnector


class EncCellRepository:
    __sql_connector = SqlConnector()

    def get_enc_cells_by_id(self, enc_cell_id):
        connection = self.__sql_connector.get_db_connection()
        cursor = connection.cursor()

        query = """
                    SELECT
                    cell_name, cell_title, ST_AsGeoJson(ST_FlipCoordinates(location)) as location
                    FROM enc_cells WHERE cell_id = %s
                    """
        cursor.execute(query, (enc_cell_id,))

        enc_cells = [build_dict(cursor, row) for row in cursor.fetchall()]
        enc_cell = enc_cells[0]
        enc_cell["location"] = json.loads(enc_cell["location"])

        connection.close()

        return enc_cell

    def get_enc_cells_search(self, search):
        if search == "":
            search = "%"
        else:
            search = f"%{search}%"

        connection = self.__sql_connector.get_db_connection()
        cursor = connection.cursor()

        query = """
                        SELECT * FROM (
                            SELECT
                            *,
                            ST_AsGeoJson(public.enc_cells.location) AS location,
                            ROUND(CAST(ST_Area(ST_Transform(location, 3857))/1000000 AS NUMERIC), 2) AS area
                            FROM enc_cells
                            WHERE cell_title LIKE %s OR cell_name LIKE %s
                        ) as enc
                        ORDER BY enc.area DESC;
                        """

        cursor.execute(
            query,
            (search, search),
        )
        enc_cells = [build_dict(cursor, row) for row in cursor.fetchall()]

        for obj in enc_cells:
            obj["location"] = json.loads(obj["location"])

        return enc_cells

    def import_enc_file(self, enc_fname):
        colnames = [
            "price_group",
            "cell_name",
            "cell_title",
            "edition",
            "edition_date",
            "update",
            "update_date",
            "unknown",
            "south_limit",
            "west_limit",
            "north_limit",
            "east_limit",
        ]

        df = pd.read_csv(enc_fname, delimiter=",", names=colnames)
        connection = self.__sql_connector.get_db_connection()
        cursor = connection.cursor()

        for index, row in df.iterrows():
            query = """INSERT INTO enc_cells(cell_name, cell_title, location)
            values(%s, %s, ST_SetSRID(ST_MakePolygon(ST_GeomFromText(%s)), 4326))"""

            west_limit = row["west_limit"]
            north_limit = row["north_limit"]
            east_limit = row["east_limit"]
            south_limit = row["south_limit"]

            linestring = (
                f"LINESTRING({west_limit} {north_limit}, {east_limit} {north_limit}, {east_limit} {south_limit}, "
                f"{west_limit} {south_limit}, {west_limit} {north_limit})"
            )

            cursor.execute(
                query,
                (
                    row["cell_name"],
                    row["cell_title"],
                    linestring,
                ),
            )

        connection.commit()
        connection.close()
