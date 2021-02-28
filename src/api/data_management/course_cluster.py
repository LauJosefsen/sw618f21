from pprint import pprint

from model.ais_data_entry import AisDataEntry
from model.ais_point import AisPoint
import geopy.distance


def cluster_ais_points_courses(points: list[AisDataEntry]) -> list[AisDataEntry]:
    """
    :param points: Input points have the same MMSI, and are always sorted by timestamp.
    """
    offset = 10  # in nautical miles
    scalar = 1.1  # multiplier of expected distance.

    if len(points) == 0:
        return []

    course = [points[0]]
    last_point = points[0]
    for point in points[1:]:
        distance_to_last_point = geopy.distance.distance(
            (last_point.latitude, last_point.longitude),
            (point.latitude, point.longitude),
        ).nautical

        last_point.sog = 2
        expected_distance = (
            last_point.sog
            * (point.timestamp - last_point.timestamp).total_seconds()
            / 3600
        )

        if expected_distance * scalar + offset < distance_to_last_point:
            continue
        course.append(point)
        last_point = point
    return course
