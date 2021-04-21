import configparser
import csv
import json
import os
import statistics
from datetime import datetime

import d6tstack.utils
import numpy as np
import pandas as pd
import psycopg2
import tqdm as tqdm
from joblib import Parallel, delayed
from psycopg2.extensions import AsIs

from data_management.course_cluster import space_data_preprocessing
from model.ais_point import AisPoint


class AisDataService:
    # Database connection:
    config = configparser.ConfigParser()
    config.read("sql.ini")

    __database = config["sql"]["database"]
    __user = config["sql"]["user"]
    __pasword = config["sql"]["password"]
    __host = config["sql"]["host"]
    __port = config["sql"]["port"]

    # used for psycopg2
    dsn = f"dbname={__database} user={__user} password={__pasword} host={__host} port={__port}"
    # used for d6tstack utilities when importing csv files.
    cfg_uri_psql = (
        f"postgresql+psycopg2://{__user}:{__pasword}@{__host}:{__port}/{__database}"
    )

    def fetch_all_limit(self, table_name, limit, offset=0):
        connection = psycopg2.connect(dsn=self.dsn)
        cursor = connection.cursor()
        query = "SELECT * FROM public.%s LIMIT %s OFFSET %s;"

        cursor.execute(query, (AsIs(table_name), limit, offset))

        return [AisDataService.__build_dict(cursor, row) for row in cursor.fetchall()]

    def fetch_specific_limit(self, col_names, table_name, limit, offset):
        connection = psycopg2.connect(dsn=self.dsn)
        cursor = connection.cursor()
        query = "SELECT %s FROM public.%s LIMIT %s OFFSET %s;"

        cursor.execute(query, (AsIs(col_names), AsIs(table_name), limit, offset))

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
            "east_limit",
        ]

        df = pd.read_csv(enc_fname, delimiter=",", names=colnames)
        connection = psycopg2.connect(dsn=self.dsn)
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
        path_list = [
            entry.path
            for entry in os.scandir("./import")
            if not entry.is_dir() and ".csv" in entry.name
        ]

        Parallel(n_jobs=16)(delayed(self.import_csv_file)(path) for path in path_list)

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

    def get_enc_cells(self, area_limits=None, search=""):

        if area_limits is None:
            area_limits = []
        if search == "":
            search = "%"
        else:
            search = f"%{search}%"

        connection = psycopg2.connect(dsn=self.dsn)
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
        data = [AisDataService.__build_dict(cursor, row) for row in cursor.fetchall()]

        for obj in data:
            obj["location"] = json.loads(obj["location"])

        filtered_data = []
        for enc in data:
            for limit in area_limits:
                if limit[0] < int(enc["area"]) < limit[1]:
                    filtered_data.append(enc)

        return filtered_data

    def get_tracks(self, limit, offset, simplify_tolerance=0, search_mmsi=None):
        connection = psycopg2.connect(dsn=self.dsn)
        cursor = connection.cursor()

        query = """
        SELECT
            t.id, t.ship_mmsi AS mmsi, MIN(p.timestamp) AS timestamp_begin,
            MAX(p.timestamp) AS timestamp_end,
            ST_AsGeoJson(ST_FlipCoordinates(
                ST_Simplify(ST_MakeLine(p.location ORDER BY p.timestamp), %s)
                )) AS coordinates
        FROM public.track AS t
        JOIN public.points AS p ON t.id=p.track_id
        WHERE t.ship_mmsi IN (SELECT mmsi FROM SHIP as s WHERE
            (SELECT count(*) FROM track WHERE ship_mmsi = s.mmsi) > 1)
        AND (%s OR t.ship_mmsi = %s)
        GROUP BY t.id, t.ship_mmsi
        LIMIT %s OFFSET %s;
        """

        cursor.execute(
            query,
            (
                simplify_tolerance,
                True if search_mmsi is None else False,
                search_mmsi,
                limit,
                offset,
            ),
        )
        data = [AisDataService.__build_dict(cursor, row) for row in cursor.fetchall()]

        cursor.close()
        connection.close()

        for row in data:
            row["coordinates"] = json.loads(row["coordinates"])["coordinates"]

        return data

    def cluster_points(self):
        connection = psycopg2.connect(dsn=self.dsn)
        cursor = connection.cursor()

        # Lets remove all the previous clustering.
        cursor.execute("TRUNCATE ship RESTART IDENTITY CASCADE")

        query = """
            SELECT DISTINCT mmsi FROM public.data WHERE mmsi < 111000000 OR mmsi > 111999999
        """
        cursor.execute(query)
        mmsi_list = cursor.fetchall()

        connection.commit()
        connection.close()

        self.__before_rule_coordinates()
        Parallel(n_jobs=16)(delayed(self.cluster_mmsi)(mmsi) for mmsi in mmsi_list)
        # [self.cluster_mmsi(mmsi) for mmsi in mmsi_list]

        connection = psycopg2.connect(dsn=self.dsn)
        cursor = connection.cursor()
        cursor.execute(
            """
                DELETE FROM ship WHERE mmsi IN
                (SELECT mmsi FROM SHIP as s WHERE (SELECT count(*) FROM track WHERE ship_mmsi = s.mmsi) = 0)
            """
        )

        connection.commit()
        connection.close()

    def __before_rule_coordinates(self):
        connection = psycopg2.connect(dsn=self.dsn)
        cursor = connection.cursor()

        cursor.execute("TRUNCATE data_error_rate")

        query_inserts = """
            WITH error_rates AS (
            SELECT
                count(DISTINCT mmsi) as begin_mmsi,
                count(*) as begin_point,
                count(DISTINCT mmsi) FILTER
                    (
                        WHERE mmsi < 111000000 OR mmsi > 111999999
                    ) as after_sar_mmsi,
                count(*) FILTER
                    (
                        WHERE mmsi < 111000000 OR mmsi > 111999999
                    ) as after_sar_point,
                count(DISTINCT mmsi) FILTER
                    (
                        WHERE  mmsi < 111000000 OR mmsi > 111999999
                        AND
                        (
                            mobile_type = 'Class A' OR mobile_type = 'Class B'
                        )
                    ) as after_ship_type_mmsi,
                count(*) FILTER
                    (
                        WHERE  mmsi < 111000000 OR mmsi > 111999999
                        AND
                        (
                            mobile_type = 'Class A' OR mobile_type = 'Class B'
                        )
                    ) as after_ship_type_point,
                count(DISTINCT mmsi) FILTER
                    (
                        WHERE mmsi < 111000000 OR mmsi > 111999999
                        AND NOT
                        (
                            (
                                longitude > 180 OR longitude < -180 OR latitude > 90 OR latitude < -90
                            )
                        )
                    ) as after_invalid_coord_mmsi,
                count(*) FILTER
                    (
                        WHERE mmsi < 111000000 OR mmsi > 111999999
                        AND NOT
                        (
                            (
                                longitude > 180 OR longitude < -180 OR latitude > 90 OR latitude < -90
                            )
                        )
                    ) as after_invalid_coord_point,
                count(DISTINCT mmsi) FILTER
                    (
                        WHERE
                        mmsi < 111000000 OR mmsi > 111999999
                        AND NOT
                        (
                            (
                                longitude > 180 OR longitude < -180 OR latitude > 90 OR latitude < -90
                            )
                            AND NOT
                            (
                                mobile_type = 'Class A' OR mobile_type = 'Class B'
                            )
                        )
                    ) as after_invalid_coord_and_ship_type_mmsi,
                count(*) FILTER
                    (
                        WHERE
                        mmsi < 111000000 OR mmsi > 111999999
                        AND NOT
                        (
                            (
                                longitude > 180 OR longitude < -180 OR latitude > 90 OR latitude < -90
                            )
                            AND NOT
                            (
                                mobile_type = 'Class A' OR mobile_type = 'Class B'
                            )
                        )
                    ) as after_invalid_coord_and_ship_type_point
            FROM DATA
            )
            INSERT INTO data_error_rate (
                rule_name,
                mmsi_count_before,
                mmsi_count_after,
                point_count_before,
                point_count_after
            ) VALUES
            (
                'Non-valid-coordinates',
                (SELECT after_sar_mmsi FROM error_rates),
                (SELECT after_invalid_coord_mmsi FROM error_rates),
                (SELECT after_sar_point FROM error_rates),
                (SELECT after_invalid_coord_point FROM error_rates)
            ),(
                'shipType',
                (SELECT after_sar_mmsi FROM error_rates),
                (SELECT after_ship_type_mmsi FROM error_rates),
                (SELECT after_sar_point FROM error_rates),
                (SELECT after_ship_type_point FROM error_rates)
            ),(
                'Non-valid-coordinates/shipType',
                (SELECT after_sar_mmsi FROM error_rates),
                (SELECT after_invalid_coord_and_ship_type_mmsi FROM error_rates),
                (SELECT after_ship_type_point FROM error_rates),
                (SELECT after_invalid_coord_and_ship_type_point FROM error_rates)
           ),(
                'mmsiIsSar',
                (SELECT begin_mmsi FROM error_rates),
                (SELECT after_sar_mmsi FROM error_rates),
                (SELECT begin_point FROM error_rates),
                (SELECT after_sar_point FROM error_rates)
            ),(
                'thresholdCompleteness',
                0,
                0,
                0,
                0
            )
        """

        cursor.execute(query_inserts)

        connection.commit()
        connection.close()

    def cluster_mmsi(self, mmsi):
        connection = psycopg2.connect(dsn=self.dsn)
        cursor = connection.cursor()

        # make a new ship, and cluster as normal
        query = """
                    INSERT INTO public.ship
                    (MMSI, IMO, mobile_type, callsign, name, ship_type, width, length, draught, a, b, c, d)
                    SELECT MMSI, IMO, mobile_type, callsign, name, ship_type, width, length, draught, a, b, c, d
                    FROM public.data WHERE mmsi= %s LIMIT 1 RETURNING mmsi
                    """

        cursor.execute(query, tuple(mmsi))
        ship_id = cursor.fetchall()[0]

        query = """
                    SELECT mmsi, timestamp, longitude, latitude, rot,
                    sog, cog, heading, position_fixing_device_type FROM public.data
                    WHERE mmsi = %s AND
                    (mobile_type = 'Class A' OR mobile_type = 'Class B') AND
                    longitude <= 180 AND longitude >=-180 AND
                    latitude <= 90 AND latitude >= -90 ORDER BY timestamp
                """

        cursor.execute(query, tuple(mmsi))
        points = [
            AisPoint(**point_dict)
            for point_dict in [
                AisDataService.__build_dict(cursor, row) for row in cursor.fetchall()
            ]
        ]

        count_before = len(points)
        # After method which looks at points
        tracks = space_data_preprocessing(points)

        count = sum(len(track) for track in tracks)

        update_threshold_query = """
        UPDATE data_error_rate SET
            mmsi_count_before = mmsi_count_before + 1,
            mmsi_count_after = mmsi_count_after + %s,
            point_count_before = point_count_before + %s,
            point_count_after = point_count_after + %s
        WHERE rule_name = 'thresholdCompleteness';
        """
        cursor.execute(
            update_threshold_query, (0 if len(tracks) == 0 else 1, count_before, count)
        )

        # insert tracks and points:
        self.__insert_tracks(ship_id, tracks, cursor)

        connection.commit()
        connection.close()

    @staticmethod
    def __insert_tracks(ship_id, tracks, cursor):
        tracks = [track for track in tracks if len(track) > 0]

        for index, course in enumerate(tracks):
            # insert course
            query = """
                            INSERT INTO public.track (ship_mmsi) VALUES (%s) RETURNING id;
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
                        point.position_fixing_device_type,
                    ),
                )
        pass

    def make_heatmap(self, eps, minpoints):
        connection = psycopg2.connect(dsn=self.dsn)
        cursor = connection.cursor()
        query = """
                        SELECT name, ST_ClusterDBSCAN(geom, eps := %s, minpoints := %s)
                """
        cursor.execute(query, eps, minpoints)

    def find_ais_time_median(self):
        print("starting")
        connection = psycopg2.connect(dsn=self.dsn)
        cursor = connection.cursor()
        query = """SELECT DISTINCT mmsi FROM public.data"""
        cursor.execute(query)
        mmsi_list = cursor.fetchall()

        time_differences = []

        medians = []

        for index, mmsi in enumerate(tqdm.tqdm(mmsi_list)):
            query = """SELECT * FROM public.data WHERE mmsi = %s ORDER BY timestamp"""
            cursor.execute(query, mmsi)
            points = [
                AisDataService.__build_dict(cursor, row) for row in cursor.fetchall()
            ]
            time_differences.append([])
            if len(points) < 100:
                continue

            i = 0
            for i, point in enumerate(points):
                if (
                    i < len(points) - 2
                    and point["timestamp"].date() == points[i + 1]["timestamp"].date()
                ):
                    time_differences[index].append(
                        self.find_time_difference(
                            point["timestamp"], points[i + 1]["timestamp"]
                        )
                    )
                else:
                    continue
        print("finding medians")
        for item in time_differences:
            if item:
                medians.append(statistics.median(item))

        with open("time_differences.csv", "w") as f:
            write = csv.writer(f)
            write.writerow(medians)

        return medians

    def find_time_difference(self, a, b):
        return int((b - a).total_seconds())

    def simple_heatmap(self, enc_cell_id: int):
        connection = psycopg2.connect(dsn=self.dsn)
        cursor = connection.cursor()
        query = """
                WITH heatmap_data AS (
                    SELECT * FROM public.heatmap_10m as heatmap
                    JOIN enc_cells as enc on st_contains(enc.location, heatmap.grid_point)
                    WHERE enc.cell_id = %s
                )
                SELECT
                    ST_AsGeoJson(ST_FlipCoordinates(grid_point)) as grid_point,
                    (count*100.0/(SELECT MAX(count) FROM heatmap_data)) as intensity
                FROM heatmap_data
            """
        cursor.execute(query, (enc_cell_id,))

        points = [AisDataService.__build_dict(cursor, row) for row in cursor.fetchall()]

        query = """
                    SELECT
                    cell_name, cell_title, ST_AsGeoJson(ST_FlipCoordinates(location)) as location
                    FROM enc_cells WHERE cell_id = %s
                    """
        cursor.execute(query, (enc_cell_id,))

        enc_cells = [
            AisDataService.__build_dict(cursor, row) for row in cursor.fetchall()
        ]
        if len(enc_cells) != 1:
            return {}
        enc_cell = enc_cells[0]
        enc_cell["location"] = json.loads(enc_cell["location"])

        connection.close()

        for point in points:
            point["grid_point"] = json.loads(point["grid_point"])

        points_formatted = [
            [
                point["grid_point"]["coordinates"][0],
                point["grid_point"]["coordinates"][1],
                point["intensity"],
            ]
            for point in points
        ]

        return {"enc": enc_cell, "heatmap_data": points_formatted}
