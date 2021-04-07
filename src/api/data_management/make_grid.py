import shapely.geometry
import pyproj




def make_grid(sw: shapely.geometry.Point, ne: shapely.geometry.Point, step_size: float):
    # Set up projections
    p_ll = pyproj.Proj(init='epsg:4326')
    p_mt = pyproj.Proj(init='epsg:3857') # metric; same as EPSG:900913


    # Project corners to target projection
    transformed_sw = pyproj.transform(p_ll, p_mt, sw.x, sw.y) # Transform NW point to 3857
    transformed_ne = pyproj.transform(p_ll, p_mt, ne.x, ne.y) # .. same for SE

    # Iterate over 2D area
    gridpoints = []
    x = transformed_sw[0]
    while x < transformed_ne[0]:
        y = transformed_sw[1]
        while y < transformed_ne[1]:
            p = shapely.geometry.Point(pyproj.transform(p_mt, p_ll, x, y))
            gridpoints.append([p.y, p.x])
            y += step_size
        x += step_size

    return gridpoints