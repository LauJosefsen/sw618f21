import os
from datetime import datetime

import d6tstack.utils
import numpy as np
import pandas as pd
import psycopg2
from geomet import wkt

from data_management.course_cluster import cluster_ais_points_courses
from data_management.clean_points import is_point_valid
from model.ais_data_entry import AisDataEntry


class AisDataService:
    dsn = "dbname=ais user=postgres password=password host=db"

    def __init__(self):
        pass

    def fetch_limit(self, limit, offset=0):
        connection = psycopg2.connect(dsn=self.dsn)
        cursor = connection.cursor()
        query = "SELECT * FROM public.data LIMIT %s OFFSET %s;"

        cursor.execute(query, (limit, offset))
        return [AisDataService.__build_dict(cursor, row) for row in cursor.fetchall()]

    def import_ais_data(self):
        print("Importing ais data..")
        for entry in os.scandir("./import"):
            if not entry.is_dir() and ".csv" in entry.name:
                num_lines = sum(1 for line in open(entry.path))
                print(f"Importing {entry.name} ({num_lines} lines)")
                self.import_csv_file(entry.path)
                print(f"Done importing {entry.name}")

    def apply(self, obj):
        obj.replace(np.nan, None)

        new_dfg = pd.DataFrame()
        new_dfg["timestamp"] = pd.to_datetime(
            obj["# Timestamp"], format="%d/%m/%Y %H:%M:%S"
        )
        new_dfg["mobile_type"] = (
            obj["Type of mobile"].astype(str).apply(self.apply_string_format)
        )
        new_dfg["mmsi"] = obj["MMSI"].astype(int)
        new_dfg["latitude"] = obj["Latitude"].astype(float)
        new_dfg["longitude"] = obj["Longitude"].astype(float)
        new_dfg["nav_stat"] = (
            obj["Navigational status"].astype(str).apply(self.apply_string_format)
        )
        new_dfg["rot"] = obj["ROT"].astype(float)
        new_dfg["sog"] = obj["SOG"].astype(float)
        new_dfg["cog"] = obj["COG"].astype(float)
        new_dfg["heading"] = obj["Heading"].astype(float)
        new_dfg["imo"] = obj["IMO"].astype(str).apply(self.apply_string_format)
        new_dfg["callsign"] = (
            obj["Callsign"].astype(str).apply(self.apply_string_format)
        )
        new_dfg["name"] = obj["Name"].astype(str).apply(self.apply_string_format)
        new_dfg["ship_type"] = (
            obj["Ship type"].astype(str).apply(self.apply_string_format)
        )
        new_dfg["cargo_type"] = (
            obj["Cargo type"].astype(str).apply(self.apply_string_format)
        )
        new_dfg["width"] = obj["Width"].astype(float)
        new_dfg["length"] = obj["Length"].astype(float)
        new_dfg["position_fixing_device_type"] = (
            obj["Type of position fixing device"]
            .astype(str)
            .apply(self.apply_string_format)
        )
        new_dfg["draught"] = obj["Draught"].astype(float)
        new_dfg["destination"] = (
            obj["Destination"].astype(str).apply(self.apply_string_format)
        )
        new_dfg["eta"] = obj["ETA"].astype(str).apply(self.apply_datetime_if_not_none)
        new_dfg["data_src_type"] = (
            obj["Data source type"].astype(str).apply(self.apply_string_format)
        )
        new_dfg["a"] = obj["A"].astype(float)
        new_dfg["b"] = obj["B"].astype(float)
        new_dfg["d"] = obj["D"].astype(float)
        new_dfg["c"] = obj["C"].astype(float)

        new_dfg.where(new_dfg.notnull(), None)

        return new_dfg

    @staticmethod
    def apply_string_format(str_input: str):
        if str_input == "nan":
            return None
        str_input = str_input.replace("\\", "\\\\")
        str_input = str_input.replace(",", r"\,")
        return str_input

    @staticmethod
    def apply_datetime_if_not_none(input):
        if input == "nan":
            return None
        return datetime.strptime(input, "%d/%m/%Y %H:%M:%S") if input else None

    def import_csv_file(self, csv_fname):
        print(csv_fname)

        cfg_uri_psql = "postgresql+psycopg2://postgres:password@db/ais"

        d6tstack.combine_csv.CombinerCSV(
            [csv_fname], apply_after_read=self.apply, add_filename=False
        ).to_psql_combine(cfg_uri_psql, "public.data", if_exists="append")

    @staticmethod
    def __build_dict(cursor, row):
        x = {}
        for key, col in enumerate(cursor.description):
            x[col[0]] = row[key]
        return x

    def get_routes(self, limit, offset):
        connection = psycopg2.connect(dsn=self.dsn)
        cursor = connection.cursor()
        query = """
            SELECT
            c.mmsi, MIN(p.timestamp) as begin,
            MAX(p.timestamp) as end, ST_AsTexT(ST_MakeLine(p.location)) as linestring
            FROM public.ais_course AS c JOIN
            (SELECT * FROM public.ais_points ORDER BY timestamp) as p ON c.id=p.ais_course_id
            GROUP BY c.id LIMIT %s OFFSET %s;"""

        cursor.execute(query, (limit, offset))

        data = [AisDataService.__build_dict(cursor, row) for row in cursor.fetchall()]

        for row in data:
            row["coordinates"] = wkt.loads(row["linestring"])["coordinates"]
            row.pop("linestring")

        return data

    def cluster_points(self):
        connection = psycopg2.connect(dsn=self.dsn)
        cursor = connection.cursor()
        cursor.execute("START TRANSACTION;")
        query = """SELECT mmsi FROM public.data GROUP BY mmsi"""
        cursor.execute(query)
        mmsi_list = cursor.fetchall()

        for mmsi in mmsi_list:
            mmsi = mmsi[0]
            query = """SELECT * FROM public.data WHERE mmsi = %s ORDER BY timestamp"""
            cursor.execute(query, tuple([str(mmsi)]))
            mmsi_points = [
                AisDataEntry(**AisDataService.__build_dict(cursor, row))
                for row in cursor.fetchall()
            ]

            mmsi_points = [point for point in mmsi_points if is_point_valid(point)]

            mmsi_points = cluster_ais_points_courses(mmsi_points)

            # insert course
            query = """
                INSERT INTO public.ais_course (mmsi) VALUES (%s);
                SELECT currval(pg_get_serial_sequence('public.ais_course','id'));
            """
            cursor.execute(query, tuple([str(mmsi)]))
            inserted_id = cursor.fetchall()[0][0]

            # insert points
            for point in mmsi_points:
                query = """
                    INSERT INTO public.ais_points
                    (mmsi, timestamp, location, rot, sog, cog, heading, ais_course_id)
                     VALUES (%s, %s, ST_SetSRID(ST_Point(%s, %s), 4326), %s, %s, %s, %s, %s)"""
                cursor.execute(
                    query,
                    (
                        point.mmsi,
                        point.timestamp,
                        point.longitude,
                        point.latitude,
                        point.rot,
                        point.sog,
                        point.cog,
                        point.heading,
                        inserted_id,
                    ),
                )

        cursor.execute("COMMIT;")
