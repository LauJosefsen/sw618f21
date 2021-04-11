import timeit

import geopy
import geopy.distance
import pyproj
import shapely
from pyproj import Transformer
from shapely.geometry import Polygon

def make_grid_mercator(sw: geopy.point, ne: geopy.point, horizontal_steps: int):
    p_ll = pyproj.Proj(init="epsg:4326")
    p_mt = pyproj.Proj(init="epsg:3857")

    transformer = Transformer.from_crs(3857, 4326)

    sw = pyproj.transform(
        p_ll, p_mt, sw.longitude, sw.latitude
    )  # Transform NW point to 3857
    ne = pyproj.transform(p_ll, p_mt, ne.longitude, ne.latitude)  # .. same for SE

    horizontal_distance = ne[1] - sw[1]
    vertical_distance = ne[0] - sw[0]

    horizontal_points = horizontal_steps
    vertical_points = vertical_distance / horizontal_distance * horizontal_steps

    horizontal_stepsize = horizontal_distance / horizontal_points
    vertical_stepsize = vertical_distance / vertical_points

    grid = []
    south = sw[1]
    while south < ne[1]:
        north_point = south + vertical_stepsize

        cur_l = sw[0]
        while cur_l < ne[0]:
            east_point = cur_l + horizontal_stepsize

            grid.append(shapely.geometry.mapping(Polygon(
                [
                    transformer.transform(cur_l, south),  # sw
                    transformer.transform(cur_l, north_point),  # nw
                    transformer.transform(east_point, north_point),  # ne
                    transformer.transform(east_point, south)  # se
                ]
            )))
            cur_l = east_point

        south = north_point

    return grid


def make_grid_meters(sw: geopy.point, ne: geopy.point, step_size: float):
    start = timeit.timeit()

    d = geopy.distance.distance(meters=step_size)

    grid = []
    current = sw
    while current.latitude < ne.latitude:
        # Save how far step_size is in longitude at this latitude
        temp = d.destination(point=current, bearing=90)
        longitude_difference = temp.longitude - current.longitude

        # Increase latitude:
        next_point = d.destination(point=current, bearing=0)

        # Lets find out the total distance:
        cur_l = current.longitude
        while cur_l < ne.longitude:
            cur_l = cur_l + longitude_difference
        distance = cur_l - current.longitude
        reg_distance = ne.longitude - current.longitude
        overshoot = distance-reg_distance

        cur_l = current.longitude - (overshoot/2)
        while cur_l < ne.longitude:
            east_point = cur_l + longitude_difference

            grid.append(shapely.geometry.mapping(Polygon(
                [
                    [current.latitude, cur_l],  # sw
                    [next_point.latitude, cur_l],  # nw
                    [next_point.latitude, east_point],  # ne
                    [current.latitude, east_point]  # se
                ]
            )))
            cur_l = east_point

        current = next_point

    end = timeit.timeit()
    print(end - start)

    return grid
