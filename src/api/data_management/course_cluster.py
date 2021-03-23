import geopy.distance

from model.ais_point import AisPoint


def space_data_preprocessing(
    track_points: list[AisPoint],
    threshold_completeness=20,
    threshold_space=25,
) -> list[list[AisPoint]]:
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

    subtracks_space = partition(track_points, threshold_space)
    tracks = association(subtracks_space, threshold_space, threshold_completeness)

    tracks = [
        subtrack for subtrack in tracks if len(subtrack) >= threshold_completeness
    ]
    return tracks


def partition(
    track_points: list[AisPoint], threshold_space: int
) -> list[list[AisPoint]]:
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
        difference_value = calc_difference_value(previous_track_point, point)

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
    track_points: list[list[AisPoint]], threshold_space, threshold_completeness
) -> list[list[AisPoint]]:
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
                association_value = calc_difference_value(boat[-1], track[0])

                if abs(association_value) < threshold_space:
                    boat.extend(track)
                    track_points.pop(index)

        if len(boat) >= threshold_completeness:
            output.append(boat)

    return output


def calc_difference_value(a, b):
    """
    Calculates the difference between the actual speed compared to the expected speed in knots
    :param a:
    :param b:
    :return: Difference in speed in knots
    """

    if abs((b.timestamp - a.timestamp).total_seconds()) > 9000:
        return 99999999999

    distance = geopy.distance.distance(
        (a.location[1], a.location[0]),
        (b.location[1], b.location[0]),
    ).nautical

    if distance <= 0.26:
        return 0

    actual_speed = get_speed_between_points(a, b)

    if a.sog is None:
        return 999999  # todo
    return actual_speed - a.sog


def assign_calculated_sog_if_sog_not_exists(points: list[AisPoint]):
    """
    In case SOG is not defined, we set an approximate value by calculating SOG.
    :param points: List of points
    :return: None
    """
    if len(points) == 0:
        return
    # last_point = points[0]
    for point in points[0:]:  # todo 1
        if point.sog:
            continue
        # actual_speed = get_speed_between_points(last_point, point) todo

        point.calc_sog = 20  # min(200, actual_speed)


def get_speed_between_points(a, b):
    """
    Calculate speed between points based on distance over time.
    :param a:
    :param b:
    :return: Speed in knots
    """
    distance = geopy.distance.distance(
        (a.location[1], a.location[0]),
        (b.location[1], b.location[0]),
    ).nautical
    time_distance = (b.timestamp - a.timestamp).total_seconds() / 3600.0
    if time_distance == 0:
        time_distance = 1
    actual_speed = distance / time_distance
    return actual_speed
