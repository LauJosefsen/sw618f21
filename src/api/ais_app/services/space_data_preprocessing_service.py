import configparser
import math
import multiprocessing
from datetime import datetime

import numpy as np
import geopy.distance
import pandas as pd
from psycopg2.extras import execute_values

from ais_app.helpers import build_dict
from ais_app.repository.sql_connector import SqlConnector


class SpaceDataPreprocessingService:
    class Consumer(multiprocessing.Process):
        def __init__(self, task_queue, result_queue):
            multiprocessing.Process.__init__(self)
            self.failed_mmsi = result_queue
            self.task_queue = task_queue

        def run(self):
            conn = SqlConnector().get_db_connection()
            conn.set_session(autocommit=True)

            sdps = SpaceDataPreprocessingService()
            while True:
                next_task = self.task_queue.get()
                if next_task is None:
                    print("Tasks Complete")
                    self.task_queue.task_done()
                    break

                success = sdps.cluster_mmsi(next_task, conn)
                self.task_queue.task_done()
                if not success:
                    self.failed_mmsi.put(next_task)
            conn.close()
            return

    sql_connector = SqlConnector()

    def __init__(self):
        config = configparser.ConfigParser()
        config.read("config.ini")

        self.threshold_completeness = int(
            config["space_data_preprocessing"]["threshold_completeness"]
        )
        self.threshold_space = int(
            config["space_data_preprocessing"]["threshold_space"]
        )
        self.split_time = int(config["space_data_preprocessing"]["split_time"])
        self.min_dist_to_compare = float(
            config["space_data_preprocessing"]["min_dist_to_compare"]
        )

    def cluster_points(self):
        connection = self.sql_connector.get_db_connection()
        cursor = connection.cursor()

        # Lets remove all the previous clustering.
        cursor.execute("TRUNCATE ship RESTART IDENTITY CASCADE")

        print("[CLUSTER] Cleared previous cluster.")

        query = """
            SELECT DISTINCT mmsi FROM public.data WHERE (mmsi < 111000000 OR mmsi > 111999999)
        """
        cursor.execute(query)
        mmsi_list = cursor.fetchall()

        print("[CLUSTER] Got mmsi distinct.")

        self.__before_invalid_coords_and_ship_types_and_intersection(cursor)

        connection.commit()
        connection.close()

        print("[CLUSTER] Cleared error_rates.")

        # append none to signal end of queue.
        mmsi_list.append(None)
        self.__cluster_mmsi_list(mmsi_list)

        connection = self.sql_connector.get_db_connection()
        cursor = connection.cursor()

        cursor.execute("REFRESH MATERIALIZED VIEW track_with_geom")
        cursor.execute(
            "REFRESH MATERIALIZED VIEW track_subdivided_with_geom_and_draught"
        )

        connection.commit()
        connection.close()

    @staticmethod
    def __cluster_mmsi_list(mmsi_list):
        # inspired by https://stackoverflow.com/q/7555680/10562012
        tasks = multiprocessing.JoinableQueue()
        results = multiprocessing.Queue()

        num_consumers = multiprocessing.cpu_count()

        consumers = [
            SpaceDataPreprocessingService.Consumer(tasks, results)
            for i in range(num_consumers)
        ]

        for w in consumers:
            w.start()

        for mmsi in mmsi_list:
            tasks.put(mmsi)

        for w in consumers:
            tasks.put(None)

        for w in consumers:
            w.join()

        if not results.empty():
            raise ValueError(f"{len(results)} mmsis failed processing.")

    @staticmethod
    def __before_invalid_coords_and_ship_types_and_intersection(cursor):
        cursor.execute("TRUNCATE data_error_rate")

        query_inserts = """
            WITH error_rates AS (
            SELECT
                count(DISTINCT mmsi) as begin_mmsi,
                count(*) as begin_point,
                count(DISTINCT mmsi) FILTER
                    (
                        WHERE (mmsi < 111000000 OR mmsi > 111999999)
                    ) as after_sar_mmsi,
                count(*) FILTER
                    (
                        WHERE (mmsi < 111000000 OR mmsi > 111999999)
                    ) as after_sar_point,
                count(DISTINCT mmsi) FILTER
                    (
                        WHERE  (mmsi < 111000000 OR mmsi > 111999999)
                        AND
                        (
                            mobile_type = 'Class A' OR mobile_type = 'Class B'
                        )
                    ) as after_ship_type_mmsi,
                count(*) FILTER
                    (
                        WHERE  (mmsi < 111000000 OR mmsi > 111999999)
                        AND
                        (
                            mobile_type = 'Class A' OR mobile_type = 'Class B'
                        )
                    ) as after_ship_type_point,
                count(DISTINCT mmsi) FILTER
                    (
                        WHERE (mmsi < 111000000 OR mmsi > 111999999)
                        AND NOT
                        (
                            (
                                longitude > 180 OR longitude < -180 OR latitude > 90 OR latitude < -90
                            )
                        )
                    ) as after_invalid_coord_mmsi,
                count(*) FILTER
                    (
                        WHERE (mmsi < 111000000 OR mmsi > 111999999)
                        AND NOT
                        (
                            (
                                longitude > 180 OR longitude < -180 OR latitude > 90 OR latitude < -90
                            )
                        )
                    ) as after_invalid_coord_point,
                count(DISTINCT mmsi) FILTER
                    (
                        WHERE (mmsi < 111000000 OR mmsi > 111999999)
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
                        WHERE (mmsi < 111000000 OR mmsi > 111999999)
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
                (SELECT after_sar_point FROM error_rates),
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

    def cluster_mmsi(self, mmsi, connection):
        try:
            cursor = connection.cursor()

            query = """
                        SELECT * FROM public.data
                        WHERE mmsi = %s AND
                        (mobile_type = 'Class A' OR mobile_type = 'Class B') AND
                        longitude <= 180 AND longitude >=-180 AND
                        latitude <= 90 AND latitude >= -90 ORDER BY timestamp
                    """

            cursor.execute(query, tuple(mmsi))
            points = [build_dict(cursor, row) for row in cursor.fetchall()]

            count_before_points = len(points)
            # After method which looks at points
            tracks = self.space_data_preprocessing(
                points, self.threshold_completeness, self.threshold_space
            )

            count_after_points = sum(len(track) for track in tracks)

            update_threshold_query = """
            UPDATE data_error_rate SET
                mmsi_count_before = mmsi_count_before + %s,
                mmsi_count_after = mmsi_count_after + %s,
                point_count_before = point_count_before + %s,
                point_count_after = point_count_after + %s
            WHERE rule_name = 'thresholdCompleteness';
            """
            cursor.execute(
                update_threshold_query,
                (
                    0 if count_before_points == 0 else 1,
                    0 if len(tracks) == 0 else 1,
                    count_before_points,
                    count_after_points,
                ),
            )

            # insert tracks and points:
            self.__insert_tracks(tracks, cursor)

            connection.commit()
            return True
        except BaseException as e:
            print(e)
            return False

    @staticmethod
    def __insert_tracks(tracks, cursor):
        tracks = [track for track in tracks if len(track) > 0]

        for index, track in enumerate(tracks):
            # insert track
            df = pd.DataFrame.from_dict(track)

            def apply_datetime_if_not_none(str_in):
                try:
                    d = datetime.strptime(str_in, "%d/%m/%Y %H:%M:%S")
                except ValueError:
                    d = None
                return d

            df["eta"] = df["eta"].astype(str).apply(apply_datetime_if_not_none)

            most_common_row = (
                df.groupby(
                    [
                        "destination",
                        "cargo_type",
                        "eta",
                        "mmsi",
                        "imo",
                        "mobile_type",
                        "callsign",
                        "name",
                        "ship_type",
                        "width",
                        "length",
                        "draught",
                        "a",
                        "b",
                        "c",
                        "d",
                    ],
                    dropna=False,
                )
                .size()
                .idxmax(skipna=False)
            )

            mcr = [
                None
                if (type(x).__module__ == np.__name__ and np.isnan(x))
                or (type(x) == float and math.isnan(x))
                else x
                for x in most_common_row
            ]

            query = """
                SELECT id FROM ship WHERE (
                    mmsi IS NOT DISTINCT FROM %s
                    AND
                    imo IS NOT DISTINCT FROM %s
                    AND
                    mobile_type IS NOT DISTINCT FROM %s
                    AND
                    callsign IS NOT DISTINCT FROM %s
                    AND
                    name IS NOT DISTINCT FROM %s
                    AND
                    ship_type IS NOT DISTINCT FROM %s
                    AND
                    width IS NOT DISTINCT FROM %s
                    AND
                    length IS NOT DISTINCT FROM %s
                    AND
                    a IS NOT DISTINCT FROM %s
                    AND
                    b IS NOT DISTINCT FROM %s
                    AND
                    c IS NOT DISTINCT FROM %s
                    AND
                    d IS NOT DISTINCT FROM %s
                )
            """
            cursor.execute(
                query,
                (
                    mcr[3],
                    mcr[4],
                    mcr[5],
                    mcr[6],
                    mcr[7],
                    mcr[8],
                    mcr[9],
                    mcr[10],
                    mcr[12],
                    mcr[13],
                    mcr[14],
                    mcr[15],
                ),
            )
            if cursor.rowcount > 0:
                ship_id = cursor.fetchone()[0]
            else:
                query = """
                INSERT INTO ship (
                    mmsi, imo, mobile_type, callsign, name, ship_type, width, length, a,b,c,d
                )
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                -- Setting name is done to make it return the existing rows id.
                -- As the only constraint is the uniqueness, this cannot risk changing anything.
                ON CONFLICT
                    (mmsi, imo, mobile_type, callsign, name, ship_type, width, length, a,b,c,d)
                DO UPDATE SET name=EXCLUDED.name
                RETURNING ID
                """
                cursor.execute(
                    query,
                    (
                        mcr[3],
                        mcr[4],
                        mcr[5],
                        mcr[6],
                        mcr[7],
                        mcr[8],
                        mcr[9],
                        mcr[10],
                        mcr[12],
                        mcr[13],
                        mcr[14],
                        mcr[15],
                    ),
                )
                ship_id = cursor.fetchone()[0]

            query = """
                INSERT INTO public.track (
                    ship_id,
                    destination,
                    cargo_type,
                    eta,
                    draught
                ) VALUES (%s, %s, %s, %s, %s) RETURNING id;
                """
            cursor.execute(query, (ship_id, mcr[0], mcr[1], mcr[2], mcr[11]))
            track_id = cursor.fetchall()[0]

            # insert points
            data = [
                (
                    track_id,
                    point["timestamp"],
                    point["longitude"],
                    point["latitude"],
                    point["rot"],
                    point["sog"],
                    point["cog"],
                    point["heading"],
                    point["position_fixing_device_type"],
                )
                for point in track
            ]
            insert_query = """
                INSERT INTO public.points
                    (
                        track_id, timestamp, location, rot,
                        sog, cog, heading, position_fixing_device_type
                    ) values %s
                """
            execute_values(
                cursor,
                insert_query,
                data,
                template="(%s, %s, ST_SetSRID(ST_Point(%s, %s),  4326), %s, %s, %s, %s, %s)",
                page_size=500,
            )

    def space_data_preprocessing(
        self,
        track_points: list,
        threshold_completeness,
        threshold_space,
    ) -> list[list]:
        """
        Takes a list of points, and returns a list of groups of points.
        Input should be only one MMSI, and sorted by timestamp.
        For further reference see: https://doi.org/10.1017/S0373463318000188
        :param track_points: List of sorted points by timestamp
        :param threshold_completeness: Minimum number of points in a course
        :param threshold_space: Maximum speed difference between points in knots to be associated.
        :return: List of groups of points
        """
        # assign_calculated_sog_if_sog_not_exists(track_points)

        subtracks_space = self.partition(track_points, threshold_space)
        tracks = self.association(
            subtracks_space, threshold_space, threshold_completeness
        )

        tracks = [
            subtrack for subtrack in tracks if len(subtrack) >= threshold_completeness
        ]
        return tracks

    def partition(self, track_points: list, threshold_space: int) -> list[list]:
        """
        Takes a list of points and partitions it into a list of groups of points based on the space threshold.
        :param track_points: List of sorted points by timestamp
        :param threshold_space: Maximum speed difference between points in knots to be associated.
        :return: List of groups of points
        """
        if len(track_points) == 0:
            return []
        previous_track_point = track_points[0]

        break_points = []

        for index, point in enumerate(track_points[1:]):
            difference_value = self.calc_difference_value(previous_track_point, point)

            if abs(difference_value) > threshold_space:
                break_points.append(index + 1)

            previous_track_point = point

        # Use the breakpoints to split track_points into subtracks..
        subtracks = []
        last_break_point = 0

        for break_point in break_points:
            subtracks.append(track_points[last_break_point:break_point])
            last_break_point = break_point
        if last_break_point != len(track_points):
            subtracks.append(track_points[last_break_point:])

        return subtracks

    def association(
        self,
        track_points: list[list],
        threshold_space,
        threshold_completeness,
    ) -> list[list]:
        """
        Associates tracks that are similar
        :param track_points: List of groups of points
        :param threshold_space: Maximum speed difference between points in knots to be associated.
        :param threshold_completeness: Minimum number of points in a course
        :return: List of groups of points
        """
        output = []
        while len(track_points) != 0:
            boat = track_points.pop(0)

            if len(track_points) != 0:
                for index, track in enumerate(track_points):
                    association_value = self.calc_difference_value(boat[-1], track[0])

                    if abs(association_value) < threshold_space:
                        boat.extend(track)
                        track_points.pop(index)

            if len(boat) >= threshold_completeness:
                output.append(boat)

        return output

    def calc_difference_value(self, a, b):
        """
        Calculates the difference between the actual speed compared to the expected speed in knots
        :param a:
        :param b:
        :return: Difference in speed in knots
        """

        if abs((b["timestamp"] - a["timestamp"]).total_seconds()) > self.split_time:
            return 2 * self.threshold_space

        distance = geopy.distance.distance(
            (a["latitude"], a["longitude"]),
            (b["latitude"], b["longitude"]),
        ).nautical

        if distance <= self.min_dist_to_compare:
            return 0

        actual_speed = self.get_speed_between_points(a, b)

        if a["sog"] is None:
            if b["sog"] is None:
                return 0 if actual_speed <= 50 else 2 * self.threshold_space
            else:
                return 2 * self.threshold_space

        return actual_speed - a["sog"]

    @staticmethod
    def get_speed_between_points(a, b):
        """
        Calculate speed between points based on distance over time.
        :param a:
        :param b:
        :return: Speed in knots
        """
        distance = geopy.distance.distance(
            (a["latitude"], a["longitude"]),
            (b["latitude"], b["longitude"]),
        ).nautical
        time_distance = (b["timestamp"] - a["timestamp"]).total_seconds() / 3600.0
        if time_distance == 0:
            time_distance = 1
        actual_speed = distance / time_distance
        return actual_speed
