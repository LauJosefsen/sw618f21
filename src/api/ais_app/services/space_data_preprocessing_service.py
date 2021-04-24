import multiprocessing
from pqdm.processes import pqdm
import geopy.distance

from ais_app.helpers import build_dict
from ais_app.repository.sql_connector import SqlConnector


class SpaceDataPreprocessingService:
    sql_connector = SqlConnector()

    def cluster_points(self):
        connection = self.sql_connector.get_db_connection()
        cursor = connection.cursor()

        # Lets remove all the previous clustering.
        # noinspection SqlWithoutWhere
        cursor.execute("UPDATE heatmap_trafic_density_1000m SET intensity = 0")
        cursor.execute("TRUNCATE ship RESTART IDENTITY CASCADE")

        print("[CLUSTER] Cleared previous cluster.")

        query = """
            SELECT DISTINCT mmsi FROM public.data WHERE mmsi < 111000000 OR mmsi > 111999999
        """
        cursor.execute(query)
        mmsi_list = cursor.fetchall()

        print("[CLUSTER] Got mmsi distinct.")

        self.__before_rule_coordinates(cursor)

        connection.commit()
        connection.close()

        print("[CLUSTER] Cleared error_rates.")
        pqdm(mmsi_list, self.cluster_mmsi, n_jobs=multiprocessing.cpu_count())
        # [self.cluster_mmsi(mmsi) for mmsi in mmsi_list]

        connection = self.sql_connector.get_db_connection()
        cursor = connection.cursor()
        cursor.execute(
            """
                DELETE FROM ship WHERE mmsi IN
                (SELECT mmsi FROM SHIP as s WHERE (SELECT count(*) FROM track WHERE ship_mmsi = s.mmsi) = 0)
            """
        )

        connection.commit()
        connection.close()

    @staticmethod
    def __before_rule_coordinates(cursor):
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

    def cluster_mmsi(self, mmsi):
        connection = self.sql_connector.get_db_connection()
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
        points = [build_dict(cursor, row) for row in cursor.fetchall()]

        count_before = len(points)
        # After method which looks at points
        tracks = self.space_data_preprocessing(points)

        count_after = sum(len(track) for track in tracks)

        update_threshold_query = """
        UPDATE data_error_rate SET
            mmsi_count_before = mmsi_count_before + 1,
            mmsi_count_after = mmsi_count_after + %s,
            point_count_before = point_count_before + %s,
            point_count_after = point_count_after + %s
        WHERE rule_name = 'thresholdCompleteness';
        """
        cursor.execute(
            update_threshold_query, (0 if len(tracks) == 0 else 1, count_before, count_after)
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
                        point['timestamp'],
                        point['longitude'],
                        point['latitude'],
                        point['rot'],
                        point['sog'],
                        point['cog'],
                        point['heading'],
                        point['position_fixing_device_type'],
                    ),
                )

    def space_data_preprocessing(
        self,
        track_points: list,
        threshold_completeness=20,
        threshold_space=25,
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

        if abs((b["timestamp"] - a["timestamp"]).total_seconds()) > 9000:
            return 99999999999

        distance = geopy.distance.distance(
            (a["latitude"], a["longitude"]),
            (b["latitude"], b["longitude"]),
        ).nautical

        if distance <= 0.26:
            return 0

        actual_speed = self.get_speed_between_points(a, b)

        if a["sog"] is None:
            if b["sog"] is None:
                return 0
            else:
                return 999999

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