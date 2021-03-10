import os
from datetime import datetime

import d6tstack.utils
import numpy as np
import pandas as pd
import psycopg2
import tqdm
from geomet import wkt

from data_management.course_cluster import (
    space_data_preprocessing,
)
from data_management.clean_points import is_point_valid
from model.ais_data_entry import AisDataEntry


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
            c.mmsi, MIN(p.timestamp) as timestamp_begin,
            MAX(p.timestamp) as timestamp_end, ST_AsTexT(ST_Simplify(ST_MakeLine(p.location),%s)) as linestring
        FROM public.ais_course AS c 
        JOIN public.ais_points_sorted as p ON c.mmsi=p.mmsi AND c.mmsi_split = p.mmsi_split 
        GROUP BY c.mmsi, c.mmsi_split;
        """

        cursor.execute(query, (simplify_tolerance, limit, offset))
        data = [AisDataService.__build_dict(cursor, row) for row in cursor.fetchall()]

        for row in data:
            row["coordinates"] = wkt.loads(row["linestring"])["coordinates"]
            row.pop("linestring")

        return data

    def cluster_points(self):
        print("Cluster begin!")
        connection = psycopg2.connect(dsn=self.dsn)
        cursor = connection.cursor()
        cursor.execute("START TRANSACTION;")
        query = """SELECT mmsi FROM public.data GROUP BY mmsi"""
        cursor.execute(query)
        mmsi_list = cursor.fetchall()

        print("Loop begin!")

        for mmsi in tqdm.tqdm(mmsi_list):
            mmsi = mmsi[0]
            query = """SELECT * FROM public.data WHERE mmsi = %s ORDER BY timestamp"""
            cursor.execute(query, tuple([str(mmsi)]))
            mmsi_points = [
                AisDataEntry(**AisDataService.__build_dict(cursor, row))
                for row in cursor.fetchall()
            ]

            mmsi_points = [point for point in mmsi_points if is_point_valid(point)]

            ais_courses = space_data_preprocessing(mmsi_points)

            # todo remove courses that are empty

            for index, course in enumerate(ais_courses):
                # insert course
                query = """
                    INSERT INTO public.ais_course (mmsi,mmsi_split) VALUES (%s, %s);
                """
                cursor.execute(query, (mmsi, index))

                # insert points
                for point in course:
                    query = """
                        INSERT INTO public.ais_points
                        (mmsi, mmsi_split, timestamp, location, rot, sog, cog, heading)
                         VALUES (%s, %s, ST_SetSRID(ST_Point(%s, %s), 4326), %s, %s, %s, %s, %s)"""
                    cursor.execute(
                        query,
                        (
                            point.mmsi,
                            index,
                            point.timestamp,
                            point.longitude,
                            point.latitude,
                            point.rot,
                            point.sog,
                            point.cog,
                            point.heading,
                        ),
                    )
        cursor.execute("COMMIT;")
