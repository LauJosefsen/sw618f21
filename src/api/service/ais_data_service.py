import csv
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
            for ade in objects:
                count = count + 1
                cur.execute(
                    """INSERT INTO ais.data (
                    timestamp, mobile_type, mmsi, latitude, longitude, nav_stat, rot, sog, cog, heading, imo, callsign,
                    name, ship_type, cargo_type, width, length, position_fixing_device_type, draught, eta,
                    data_src_type, destination, a, b, c, d) VALUES
                    (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (ade.timestamp.isoformat(), ade.mobile_type, ade.mmsi, ade.latitude, ade.longitude, ade.nav_stat,
                     ade.rot, ade.sog, ade.cog, ade.heading, ade.imo, ade.callsign, ade.name, ade.ship_type,
                     ade.cargo_type, ade.width, ade.length, ade.position_fixing_device_type, ade.draught,
                     ade.eta.isoformat() if ade.eta else None,
                     ade.data_src_type, ade.destination, ade.a, ade.b, ade.c, ade.d)
                )
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

    def import_file(self, path):

        conn = None
        try:
            conn = psycopg2.connect(self.dsn)
            cur = conn.cursor()

            with open(path) as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=',')
                line_count = 0
                columns = []
                for row in csv_reader:
                    if line_count == 0:
                        columns = row
                        line_count += 1
                    else:
                        line_count += 1
                        obj = self.create_dict_from_row(columns, row)
                        obj = self.map_dict_to_ais_data_entry(obj)
                        obj = AisDataEntry.from_dict(obj)
                        self.add_inserts_to_transaction(cur, [obj])

            conn.commit()
            # close the database communication
            cur.close()
        except psycopg2.DatabaseError as error:
            print(error)
        finally:
            if conn is not None:
                conn.close()

    @staticmethod
    def add_inserts_to_transaction(cur, objects):
        for ade in objects:
            cur.execute(
                """INSERT INTO ais.data (
                timestamp, mobile_type, mmsi, latitude, longitude, nav_stat, rot, sog, cog, heading, imo, callsign,
                name, ship_type, cargo_type, width, length, position_fixing_device_type, draught, eta,
                data_src_type, destination, a, b, c, d) VALUES
                (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (ade.timestamp.isoformat(), ade.mobile_type, ade.mmsi, ade.latitude, ade.longitude, ade.nav_stat,
                 ade.rot, ade.sog, ade.cog, ade.heading, ade.imo, ade.callsign, ade.name, ade.ship_type,
                 ade.cargo_type, ade.width, ade.length, ade.position_fixing_device_type, ade.draught,
                 ade.eta.isoformat() if ade.eta else None,
                 ade.data_src_type, ade.destination, ade.a, ade.b, ade.c, ade.d)
            )

    @staticmethod
    def create_dict_from_row(columns, row):
        obj = {}
        for index, column in enumerate(columns):
            obj[column] = row[index]
        return obj

    @staticmethod
    def map_dict_to_ais_data_entry(obj):
        mapping_dictionary = {
            "# Timestamp": "timestamp",
            "Type of mobile": "mobile_type",
            "MMSI": "mmsi",
            "Latitude": "latitude",
            "Longitude": "longitude",
            "Navigational status": "nav_stat",
            "ROT": "rot",
            "SOG": "sog",
            "COG": "cog",
            "Heading": "heading",
            "IMO": "imo",
            "Callsign": "callsign",
            "Name": "name",
            "Ship type": "ship_type",
            "Cargo type": "cargo_type",
            "Width": "width",
            "Length": "length",
            "Type of position fixing device": "position_fixing_device_type",
            "Draught": "draught",
            "Destination": "destination",
            "ETA": "eta",
            "Data source type": "data_src_type",
            "A": "a",
            "B": "b",
            "C": "c",
            "D": "d"
        }
        new_obj = {}
        for key in obj:
            new_key = mapping_dictionary[key]
            new_obj[new_key] = obj[key]

        return new_obj
