import csv
import json
import os
import statistics
import pandas as pd
import tqdm as tqdm
from psycopg2.extensions import AsIs
from ais_app.helpers import build_dict
from ais_app.repository.sql_connector import SqlConnector


class AisDataService:

    sql_connector = SqlConnector()

    def fetch_all_limit(self, table_name, limit, offset=0):
        connection = self.sql_connector.get_db_connection()
        cursor = connection.cursor()
        query = "SELECT * FROM public.%s LIMIT %s OFFSET %s;"

        cursor.execute(query, (AsIs(table_name), limit, offset))

        return [build_dict(cursor, row) for row in cursor.fetchall()]

    def fetch_specific_limit(self, col_names, table_name, limit, offset):
        connection = self.sql_connector.get_db_connection()
        cursor = connection.cursor()
        query = "SELECT %s FROM public.%s LIMIT %s OFFSET %s;"

        cursor.execute(query, (AsIs(col_names), AsIs(table_name), limit, offset))

        return [build_dict(cursor, row) for row in cursor.fetchall()]

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
        connection = self.sql_connector.get_db_connection()
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

    def get_enc_cells(self, area_limits=None, search=""):

        if area_limits is None:
            area_limits = []
        if search == "":
            search = "%"
        else:
            search = f"%{search}%"

        connection = self.sql_connector.get_db_connection()
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
        data = [build_dict(cursor, row) for row in cursor.fetchall()]

        for obj in data:
            obj["location"] = json.loads(obj["location"])

        filtered_data = []
        for enc in data:
            for limit in area_limits:
                if limit[0] < int(enc["area"]) < limit[1]:
                    filtered_data.append(enc)

        return filtered_data

    def get_tracks(self, limit, offset, simplify_tolerance=0, search_mmsi=None):
        connection = self.sql_connector.get_db_connection()
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
        data = [build_dict(cursor, row) for row in cursor.fetchall()]

        cursor.close()
        connection.close()

        for row in data:
            row["coordinates"] = json.loads(row["coordinates"])["coordinates"]

        return data

    def get_tracks_in_enc(self, enc_cell_id: int, simplify_tolerance=0):
        connection = self.sql_connector.get_db_connection()
        cursor = connection.cursor()

        query = """
        SELECT
            t.id, t.ship_mmsi AS mmsi,
            ST_AsGeoJson(ST_FlipCoordinates(
                ST_Simplify(t.geom, %s)
                )) AS coordinates
        FROM public.track_with_geom AS t
        JOIN enc_cells AS enc ON ST_Intersects(enc.location, t.geom)
        WHERE enc.cell_id = %s
        
        """

        cursor.execute(
            query,
            (simplify_tolerance, enc_cell_id),
        )
        data = [build_dict(cursor, row) for row in cursor.fetchall()]

        query = """
                            SELECT
                            cell_name, cell_title, ST_AsGeoJson(ST_FlipCoordinates(location)) as location
                            FROM enc_cells WHERE cell_id = %s
                            """
        cursor.execute(query, (enc_cell_id,))

        enc_cells = [build_dict(cursor, row) for row in cursor.fetchall()]
        if len(enc_cells) != 1:
            return {}
        enc_cell = enc_cells[0]
        enc_cell["location"] = json.loads(enc_cell["location"])

        cursor.close()
        connection.close()

        for row in data:
            row["coordinates"] = json.loads(row["coordinates"])["coordinates"]

        return {"tracks": data, "enc": enc_cell}

    def make_heatmap(self, eps, minpoints):
        connection = self.sql_connector.get_db_connection()
        cursor = connection.cursor()
        query = """
                        SELECT name, ST_ClusterDBSCAN(geom, eps := %s, minpoints := %s)
                """
        cursor.execute(query, eps, minpoints)

    def find_ais_time_median(self):
        print("starting")
        connection = self.sql_connector.get_db_connection()
        cursor = connection.cursor()
        query = """SELECT DISTINCT mmsi FROM public.data"""
        cursor.execute(query)
        mmsi_list = cursor.fetchall()

        time_differences = []

        medians = []

        for index, mmsi in enumerate(tqdm.tqdm(mmsi_list)):
            query = """SELECT * FROM public.data WHERE mmsi = %s ORDER BY timestamp"""
            cursor.execute(query, mmsi)
            points = [build_dict(cursor, row) for row in cursor.fetchall()]
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

    def trafic_density_heatmap(self, enc_cell_id: int):
        connection = self.sql_connector.get_db_connection()
        cursor = connection.cursor()
        query = """
                WITH heatmap_data AS (
                    SELECT geom, intensity FROM heatmap_trafic_density_1000m as heatmap
                    JOIN enc_cells as enc on st_contains(enc.location, heatmap.geom)
                    WHERE enc.cell_id = %s AND heatmap.intensity > 0
                )
                SELECT
                    ST_AsGeoJson(ST_FlipCoordinates(ST_Centroid(geom))) as grid_point,
                    (intensity*50000/(SELECT MAX(intensity) FROM heatmap_data)) as intensity
                FROM heatmap_data
            """
        cursor.execute(query, (enc_cell_id,))

        points = [build_dict(cursor, row) for row in cursor.fetchall()]

        query = """
                    SELECT
                    cell_name, cell_title, ST_AsGeoJson(ST_FlipCoordinates(location)) as location
                    FROM enc_cells WHERE cell_id = %s
                    """
        cursor.execute(query, (enc_cell_id,))

        enc_cells = [build_dict(cursor, row) for row in cursor.fetchall()]
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

    def simple_heatmap(self, enc_cell_id: int):
        connection = self.sql_connector.get_db_connection()
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

        points = [build_dict(cursor, row) for row in cursor.fetchall()]

        query = """
                    SELECT
                    cell_name, cell_title, ST_AsGeoJson(ST_FlipCoordinates(location)) as location
                    FROM enc_cells WHERE cell_id = %s
                    """
        cursor.execute(query, (enc_cell_id,))

        enc_cells = [build_dict(cursor, row) for row in cursor.fetchall()]
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
