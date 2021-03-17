import os
from datetime import datetime

import d6tstack.utils
import numpy as np
import pandas as pd
import psycopg2
from geomet import wkt
from psycopg2.pool import ThreadedConnectionPool

from data_management.course_cluster import space_data_preprocessing
from model.ais_point import AisPoint


class AisDataService:
    # Database connection:
    __database = "ais"
    __user = "postgres"
    __pasword = "password"
    __host = "db"

    # used for psycopg2
    dsn = f"dbname={__database} user={__user} password={__pasword} host={__host}"
    # used for d6tstack utilities when importing csv files.
    cfg_uri_psql = f"postgresql+psycopg2://{__user}:{__pasword}@{__host}/{__database}"

    def fetch_limit(self, limit, offset=0):
        connection = psycopg2.connect(dsn=self.dsn)
        cursor = connection.cursor()
        query = "SELECT * FROM public.data LIMIT %s OFFSET %s;"

        cursor.execute(query, (limit, offset))

        return [AisDataService.__build_dict(cursor, row) for row in cursor.fetchall()]

    def import_enc_data(self):
        print("Importing enc data..")
        for entry in os.scandir("./import"):
            if not entry.is_dir() and ".txt" in entry.name:
                print(f"Importing {entry.name}")
                self.import_enc_file(entry.path)
                print(f"Done importing {entry.name}")

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
            "east_limit"
        ]

        df = pd.read_csv(enc_fname, delimiter=",", names=colnames)
        connection = psycopg2.connect(dsn=self.dsn)

        for index, row in df.iterrows():
            cursor = connection.cursor()
            query = """INSERT INTO enc_cells(cell_name, cell_title, edition,
             edition_date, update, update_date, south_limit, west_limit, north_limit, east_limit) 
            values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""

            cursor.execute(query, (row['cell_name'], row['cell_title'], self.check_if_none(row, 'edition'),
                                   self.apply_date_if_not_none(str(row['edition_date'])),
                                   self.check_if_none(row, 'update'), self.apply_date_if_not_none(str(row['update_date'])),
                                   row['south_limit'],
                                   row['west_limit'], row['north_limit'],
                                   row['east_limit']))

        connection.commit()

        cursor.close()
        connection.close()

    def check_if_none(self, row, col_name):
        # Checks for missing values in col
        if pd.isna(row[col_name]):
            return 0
        else:
            return row[col_name]


    def apply_date_if_not_none(self, str_in):
        if str_in == "nan":
            return None
        return datetime.strptime(str_in, "%d/%m/%y") if str_in else None

    def import_ais_data(self):
        print("Importing ais data..")
        for entry in os.scandir("./import"):
            if not entry.is_dir() and ".csv" in entry.name:
                print(f"Importing {entry.name}")
                self.import_csv_file(entry.path)
                print(f"Done importing {entry.name}")

    def import_csv_file(self, csv_fname):
        def apply_string_format(str_input: str):
            if str_input == "nan":
                return None
            str_input = str_input.replace("\\", "\\\\")
            str_input = str_input.replace(",", r"\,")
            return str_input

        def apply_datetime_if_not_none(str_in):
            if str_in == "nan":
                return None
            return datetime.strptime(str_in, "%d/%m/%Y %H:%M:%S") if str_in else None

        def apply(obj):
            obj.replace(np.nan, None)

            new_dfg = pd.DataFrame()
            new_dfg["timestamp"] = pd.to_datetime(
                obj["# Timestamp"], format="%d/%m/%Y %H:%M:%S"
            )
            new_dfg["mobile_type"] = (
                obj["Type of mobile"].astype(str).apply(apply_string_format)
            )
            new_dfg["mmsi"] = obj["MMSI"].astype(int)
            new_dfg["latitude"] = obj["Latitude"].astype(float)
            new_dfg["longitude"] = obj["Longitude"].astype(float)
            new_dfg["nav_stat"] = (
                obj["Navigational status"].astype(str).apply(apply_string_format)
            )
            new_dfg["rot"] = obj["ROT"].astype(float)
            new_dfg["sog"] = obj["SOG"].astype(float)
            new_dfg["cog"] = obj["COG"].astype(float)
            new_dfg["heading"] = obj["Heading"].astype(float)
            new_dfg["imo"] = obj["IMO"].astype(str).apply(apply_string_format)
            new_dfg["callsign"] = obj["Callsign"].astype(str).apply(apply_string_format)
            new_dfg["name"] = obj["Name"].astype(str).apply(apply_string_format)
            new_dfg["ship_type"] = (
                obj["Ship type"].astype(str).apply(apply_string_format)
            )
            new_dfg["cargo_type"] = (
                obj["Cargo type"].astype(str).apply(apply_string_format)
            )
            new_dfg["width"] = obj["Width"].astype(float)
            new_dfg["length"] = obj["Length"].astype(float)
            new_dfg["position_fixing_device_type"] = (
                obj["Type of position fixing device"]
                    .astype(str)
                    .apply(apply_string_format)
            )
            new_dfg["draught"] = obj["Draught"].astype(float)
            new_dfg["destination"] = (
                obj["Destination"].astype(str).apply(apply_string_format)
            )
            new_dfg["eta"] = obj["ETA"].astype(str).apply(apply_datetime_if_not_none)
            new_dfg["data_src_type"] = (
                obj["Data source type"].astype(str).apply(apply_string_format)
            )
            new_dfg["a"] = obj["A"].astype(float)
            new_dfg["b"] = obj["B"].astype(float)
            new_dfg["d"] = obj["D"].astype(float)
            new_dfg["c"] = obj["C"].astype(float)
            new_dfg["is_processed"] = pd.Series([False for _ in range(len(new_dfg["mmsi"]))], index=new_dfg.index)

            new_dfg.where(new_dfg.notnull(), None)

            return new_dfg

        print(csv_fname)

        d6tstack.combine_csv.CombinerCSV(
            [csv_fname], apply_after_read=apply, add_filename=False
        ).to_psql_combine(self.cfg_uri_psql, "public.data", if_exists="append")

    @staticmethod
    def __build_dict(cursor, row):
        x = {}
        for key, col in enumerate(cursor.description):
            x[col[0]] = row[key]
        return x

    def get_routes(self, limit, offset, simplify_tolerance=0):
        connection = psycopg2.connect(dsn=self.dsn)
        cursor = connection.cursor()
        query = """
        SELECT
            t.id, MIN(p.timestamp) as timestamp_begin,
            MAX(p.timestamp) as timestamp_end, ST_AsText(ST_FlipCoordinates(ST_MakeLine(p.location))) as linestring
        FROM public.track AS t
        JOIN public.points_sorted as p ON t.id=p.track_id
        GROUP BY t.id
        LIMIT %s OFFSET %s;
        """

        cursor.execute(query, (limit, offset))
        data = [AisDataService.__build_dict(cursor, row) for row in cursor.fetchall()]

        cursor.close()
        connection.close()

        for row in data:
            row["coordinates"] = wkt.loads(row["linestring"])["coordinates"]
            row.pop("linestring")

        return data

    # def cluster_points(self):
    #     print("Cluster begin!")
    #     connection = psycopg2.connect(dsn=self.dsn)
    #     cursor = connection.cursor()
    #     cursor.execute("START TRANSACTION;")
    #     query = """SELECT mmsi FROM public.data GROUP BY mmsi"""
    #     cursor.execute(query)
    #     mmsi_list = cursor.fetchall()
    #
    #     print("Loop begin!")
    #
    #     for mmsi in tqdm.tqdm(mmsi_list):
    #         mmsi = mmsi[0]
    #         query = """
    #         SELECT mmsi, timestamp, longitude, latitude, rot, sog, cog, heading FROM public.data
    #         WHERE mmsi = %s AND
    #         (mobile_type = 'Class A' OR mobile_type = 'Class B') AND
    #         longitude <= 180 AND longitude >=-180 AND
    #         latitude <= 90 AND latitude >= -90 ORDER BY timestamp
    #         """
    #         cursor.execute(query, tuple([str(mmsi)]))
    #         mmsi_points = [
    #             AisDataEntry(**AisDataService.__build_dict(cursor, row))
    #             for row in cursor.fetchall()
    #         ]
    #
    #         ais_courses = [
    #             ais_course
    #             for ais_course in space_data_preprocessing(mmsi_points)
    #             if len(ais_course) > 0
    #         ]
    #
    #         for index, course in enumerate(ais_courses):
    #             # insert course
    #             query = """
    #                 INSERT INTO public.ais_course (mmsi,mmsi_split) VALUES (%s, %s);
    #             """
    #             cursor.execute(query, (mmsi, index))
    #
    #             # insert points
    #             for point in course:
    #                 query = """
    #                     INSERT INTO public.ais_points
    #                     (mmsi, mmsi_split, timestamp, location, rot, sog, cog, heading)
    #                          VALUES (%s, %s, %s, ST_SetSRID(ST_Point(%s, %s), 4326), %s, %s, %s, %s)"""
    #                 cursor.execute(
    #                     query,
    #                     (
    #                         point.mmsi,
    #                         index,
    #                         point.timestamp,
    #                         point.longitude,
    #                         point.latitude,
    #                         point.rot,
    #                         point.sog,
    #                         point.cog,
    #                         point.heading,
    #                     ),
    #                 )
    #     connection.commit()
    #
    #     cursor.close()
    #     connection.close()

    def new_cluster(self):

        tcp = ThreadedConnectionPool(2, 16, self.dsn)

        # Select unique MMSI from data where is_processed is false
        connection = tcp.getconn()
        cursor = connection.cursor()
        cursor.execute("START TRANSACTION;")
        query = """SELECT mmsi FROM public.data WHERE is_processed =  False GROUP BY mmsi"""
        cursor.execute(query)
        mmsi_list = cursor.fetchall()

        # For each of these MMSI:
        for mmsi in mmsi_list:
            query = """SELECT * FROM public.ship WHERE mmsi = %s"""
            cursor.execute(query, tuple(mmsi))
            ships = cursor.fetchall()

            if len(ships) > 0:
                # do some magic connecting courses if they are indeed connected.
                pass  # todo
            else:
                # make a new ship, and cluster as normal
                query = """
                        INSERT INTO public.ship
                        (MMSI, IMO, mobile_type, callsign, name, ship_type, width, length, draught, a, b, c, d)
                        SELECT MMSI, IMO, mobile_type, callsign, name, ship_type, width, length, draught, a, b, c, d
                        FROM public.data WHERE mmsi= %s AND is_processed = False LIMIT 1 RETURNING id
                        """
                cursor.execute(query, tuple(mmsi))
                ship_id = cursor.fetchall()

                query = """
                            SELECT mmsi, timestamp, longitude, latitude, rot,
                             sog, cog, heading, position_fixing_device_type FROM public.data 
                            WHERE mmsi = %s AND 
                            (mobile_type = 'Class A' OR mobile_type = 'Class B') AND 
                            longitude <= 180 AND longitude >=-180 AND
                            latitude <= 90 AND latitude >= -90 AND is_processed = False ORDER BY timestamp
                            """
                cursor.execute(query, tuple(mmsi))
                points = [AisPoint(**point_dict) for point_dict in
                          [AisDataService.__build_dict(cursor, row) for row in cursor.fetchall()]
                          ]

                tracks = space_data_preprocessing(points)

                # insert tracks and points:
                self.__insert_tracks(ship_id, tracks, cursor)

                # mark as processed
                cursor.execute(
                    "UPDATE public.data SET is_processed = True WHERE mmsi=%s AND is_processed = False",
                    tuple(mmsi)
                )  # todo this might mark points that were not included, as they were removed as trash.

                cursor.execute("""
                                  DELETE FROM ship WHERE id IN 
                                  (SELECT id FROM SHIP as s WHERE (SELECT count(*) FROM track WHERE ship_id = s.id) = 0)
                               """
                               )

            connection.commit()

    @staticmethod
    def __insert_tracks(ship_id, tracks, cursor):
        tracks = [
            track
            for track in tracks
            if len(track) > 0
        ]

        for index, course in enumerate(tracks):
            # insert course
            query = """
                            INSERT INTO public.track (ship_id) VALUES (%s) RETURNING id;
                        """
            cursor.execute(query, tuple(ship_id))
            track_id = cursor.fetchall()[0]

            # insert points
            for point in course:
                query = """
                                INSERT INTO public.points
                                (track_id, timestamp, location, rot, sog, cog, heading, position_fixing_device_type)
                                     VALUES (%s, %s, ST_SetSRID(ST_Point(%s, %s),  4326), %s, %s, %s, %s, %s)"""
                cursor.execute(
                    query,
                    (
                        track_id,
                        point.timestamp,
                        point.location[0],
                        point.location[1],
                        point.rot,
                        point.sog,
                        point.cog,
                        point.heading,
                        point.position_fixing_device_type
                    ),
                )
        pass
