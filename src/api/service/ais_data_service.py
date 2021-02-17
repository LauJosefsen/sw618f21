import psycopg2
from typing import List

from model.ais_data_entry import AisDataEntry


class AisDataService:
    dsn = "dbname=ais user=postgres password=password host=db"

    def __init__(self):
        self.connection = psycopg2.connect(
            user="postgres",
            password="password",
            host="db",
            port="5432",
            database="ais",
        )

    def fetch_all(self):
        cursor = self.connection.cursor()
        query = "SELECT * FROM ais.data"

        cursor.execute(query)
        return [AisDataService.__build_dict(cursor, row) for row in cursor.fetchall()]

    def insert_many(self, objects: List[AisDataEntry]):
        conn = None
        try:
            conn = psycopg2.connect(self.dsn)
            cur = conn.cursor()
            # execute 1st statement
            count = 0
            for ais_data_entry in objects:
                count = count + 1
                if count > 100:
                    break
                cur.execute(
                    """INSERT INTO ais.data (
                    timestamp, mobile_type, mmsi, latitude, longitude, nav_stat, rot, sog, cog, heading, imo, callsign,
                    name, ship_type, cargo_type, width, length, position_fixing_device_type, draught, eta,
                    data_src_type, destination, a, b, c, d) VALUES
                    (%s, %s, %s, %s, %s, %s, %s, %S, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    ais_data_entry.__dict__.values()
                )
                print(f"Executed {ais_data_entry.__dict__.values()}")
            conn.commit()
            # close the database communication
            cur.close()
        except psycopg2.DatabaseError as error:
            print(error)
        finally:
            if conn is not None:
                conn.close()

    @staticmethod
    def __build_dict(cursor, row):
        x = {}
        for key, col in enumerate(cursor.description):
            x[col[0]] = row[key]
        return x
