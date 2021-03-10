from model.ais_data_entry import AisDataEntry
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


def space_data_preprocessing(
    track_points: list[AisDataEntry],
    threshold_time=10,
    threshold_completeness=1,
    threshold_space=15,
) -> list[list[AisDataEntry]]:
    assign_calculated_sog_if_sog_not_exists(track_points)
    # cleaning time data
    tracks_time = partition(track_points, threshold_time)
    # filtering of physical integrity
    tracks_time = [
        subtrack for subtrack in tracks_time if len(subtrack) >= threshold_completeness
    ]

    output = []

    # cleaning space data
    for subtrack in tracks_time:
        subtracks_space = partition(subtrack, threshold_space)
        tracks_space = association(
            subtracks_space, threshold_space, threshold_completeness
        )
        output.extend(tracks_space)
    return output


def partition(
    track_points: list[AisDataEntry], threshold_partition: int
) -> list[list[AisDataEntry]]:
    if len(track_points) == 0:
        return []
    previous_track_point = track_points[0]

    break_points = []

    for index, point in enumerate(track_points[1:]):
        difference_value = calc_difference_value(point, previous_track_point)

        if difference_value > threshold_partition:
            break_points.append(index + 1)

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
    track_points: list[list[AisDataEntry]],
    threshold_association,
    threshold_completeness,
):
    output = []
    while track_points:
        boat = track_points.pop(0)

        if track_points:
            for index, track in enumerate(track_points):
                association_value = calc_difference_value(boat[-1], track[0])

                if association_value < threshold_association:
                    boat.extend(track)
                    track_points.pop(index)

        if len(boat) >= threshold_completeness:
            output.append(boat)

    return output


def calc_difference_value(a, b):
    distance = geopy.distance.distance(
        (b.latitude, b.longitude),
        (a.latitude, a.longitude),
    ).nautical
    time_distance = (a.timestamp - b.timestamp).total_seconds() / 3600.0
    if time_distance == 0:
        time_distance = 1
    actual_speed = distance / time_distance

    if not a.sog:
        return actual_speed - a.calc_sog
    return actual_speed - a.sog


def assign_calculated_sog_if_sog_not_exists(
    points: list[AisDataEntry],
):
    if len(points) == 0:
        return
    last_point = points[0]
    for point in points[1:]:
        if point.sog:
            continue
        distance = geopy.distance.distance(
            (last_point.latitude, last_point.longitude),
            (point.latitude, point.longitude),
        ).nautical
        time_distance = (
            point.timestamp - last_point.timestamp
        ).total_seconds() / 3600.0

        if time_distance == 0:
            time_distance = 1
        actual_speed = distance / time_distance

        point.calc_sog = min(200, actual_speed)
