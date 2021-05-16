from PIL import Image, ImageDraw, ImageFont
from pykrige import OrdinaryKriging
from pyproj import Transformer
from tqdm import tqdm

from ais_app.helpers import MinMaxXy
from ais_app.repository.depth_map_repository import DepthMapRepository
import numpy as np


class DepthMapService:
    __depth_map_repository = DepthMapRepository()

    def get_within_box(self, n, s, e, w):
        return self.__depth_map_repository.get_within_box(n, s, e, w)

    def get_map_tiles(self, min_zoom: int, max_zoom: int):
        return self.__depth_map_repository.get_map_tiles(min_zoom, max_zoom)

    def get_max_depth(self):
        return self.__depth_map_repository.get_max_depth()

    def interpolate_depth_map_in_enc(self, enc_id, enc_bounds: MinMaxXy, grid_size: int):
        depth_measurement_points = self.__depth_map_repository.get_min_depth_as_points_in_enc_in_utm32n(enc_id)

        gridx = np.arange(enc_bounds.min_x, enc_bounds.max_x, grid_size)
        gridy = np.arange(enc_bounds.min_y, enc_bounds.max_y, grid_size)

        x = [depth['x'] for depth in depth_measurement_points]
        y = [depth['y'] for depth in depth_measurement_points]
        z = [depth['z'] for depth in depth_measurement_points]

        OK = OrdinaryKriging(
            x, y, z,
            variogram_model="spherical",
            enable_plotting=False,
        )

        return OK.execute("grid", gridx, gridy, n_closest_points=10, backend="loop")

    def map(self,
            x: float, in_min: float, in_max: float, out_min: float, out_max: float
    ) -> float:
        """
        Maps a float from one interval to another
        :param x: The value to map
        :param in_min: The original value's interval minimum
        :param in_max: The original value's interval maximum
        :param out_min: The new interval minimum
        :param out_max: The new interval maximum
        :return: the mapped value in the new interval
        """
        return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

    def render_interpolated(self, bounds: MinMaxXy, grid_size, tiles, depths, varians, max_varians):
        transformer = Transformer.from_crs(25832, 3857)

        for tile in tiles:
            tile_bounds = MinMaxXy.from_coords(tile['geom']['coordinates'][0])



    def insert_interpolated_depth_map(self, bounds: MinMaxXy, grid_size, depths, varians):
        # loop with index-x, index-y in depths. Varians should have the same indexes..

        self.__depth_map_repository.truncate_interpolated_depth_map()
        self.__depth_map_repository.insert_interpolated_depths(depths, varians, bounds, grid_size)

    def render_interpolated_depth_map(self, min_zoom, max_zoom):
        tiles = self.get_map_tiles(min_zoom, max_zoom)
        max_depth = self.get_max_depth() #todo use this tables max
        max_varians = 15 #todo figure this out



        for tile in tqdm(tiles):
            coordinates = tile["geom"]["coordinates"][0]
            tile_bounds = MinMaxXy.from_coords(coordinates)

            depths = self.get_within_box_interpolated(tile_bounds)

            if len(depths) == 0:
                continue

            img = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            for depth in depths:
                if depth['varians'] >= max_varians:
                    continue
                coordinates = depth["geom"]["coordinates"][0]
                bounds_relative = MinMaxXy.from_coords(coordinates)

                bounds_in_image = MinMaxXy(
                    self.map(bounds_relative.min_x, tile_bounds.min_x, tile_bounds.max_x, 0, 255),
                    self.map(bounds_relative.min_y, tile_bounds.min_y, tile_bounds.max_y, 255, 0),
                    self.map(bounds_relative.max_x, tile_bounds.min_x, tile_bounds.max_x, 0, 255),
                    self.map(bounds_relative.max_y, tile_bounds.min_y, tile_bounds.max_y, 255, 0)
                )

                min_depth = depth["depth"]
                min_depth_color = int(self.map(min_depth, 0, max_depth, 0, 255))
                color = (min_depth_color, 0, 255 - min_depth_color)

                draw.rectangle(
                    [
                        (bounds_in_image.min_x, bounds_in_image.min_y),
                        (bounds_in_image.max_x, bounds_in_image.max_y)
                    ],
                    fill=color
                )

                font = ImageFont.truetype("arial.ttf", int((bounds_in_image.max_x-bounds_in_image.min_x)/2))
                if tile['z'] >= 11:
                    draw.text(((bounds_in_image.max_x + bounds_in_image.min_x) / 2,
                               (bounds_in_image.max_y + bounds_in_image.min_y) / 2),
                              text=f"{round(depth['depth'],1)}\n{round(depth['varians'],1)}", fill='white', font=font)


            img.save(f"ais_app/tiles/{tile['z']}-{tile['x']}-{tile['y']}.png")

        return "Server go brbrbr"

    def get_within_box_interpolated(self, tile_bounds):
        return self.__depth_map_repository.get_within_box_interpolated(tile_bounds)

