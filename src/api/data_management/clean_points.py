from model.ais_data_entry import AisDataEntry


def is_point_valid(point: AisDataEntry) -> bool:
    """
    Returns true if location data of point is valid
    :param point:
    :return:
    """
    longitude = point.longitude
    latitude = point.latitude

    if -180 < longitude < 180 and -90 < latitude < 90:
        return True
    return False
