import configparser
import os

from PIL import Image, ImageDraw, ImageFont
from pykrige import OrdinaryKriging
from tqdm import tqdm
import pylab as pl

from ais_app.helpers import MinMaxXy
from ais_app.repository.depth_map_repository import DepthMapRepository
import numpy as np


class DepthMapService:
    __depth_map_repository = DepthMapRepository()

    def __init__(self):
        config = configparser.ConfigParser()
        config.read("config.ini")

        self.raw_tiles_folder = config["depth_map"]["raw_tiles_folder"]
        self.interpolated_tiles_folder = config["depth_map"][
            "interpolated_tiles_folder"
        ]

    def get_within_box(self, n, s, e, w):
        return self.__depth_map_repository.get_within_box(n, s, e, w)

    def get_map_tiles(self, min_zoom: int, max_zoom: int):
        return self.__depth_map_repository.get_map_tiles(min_zoom, max_zoom)

    def get_max_depth(self):
        return self.__depth_map_repository.get_max_depth()

    def interpolate_depth_map_in_enc(
        self, enc_id, enc_bounds: MinMaxXy, grid_size: int, downscale: int
    ):

        depth_measurement_points = (
            self.__depth_map_repository.get_min_depth_as_points_in_enc_in_utm32n(enc_id, downscale)
        )

        gridx = np.arange(enc_bounds.min_x, enc_bounds.max_x, grid_size)
        gridy = np.arange(enc_bounds.min_y, enc_bounds.max_y, grid_size)

        x = [depth["x"] for depth in depth_measurement_points]
        y = [depth["y"] for depth in depth_measurement_points]
        z = [depth["z"] for depth in depth_measurement_points]

        OK = OrdinaryKriging(
            x,
            y,
            z,
            variogram_model="spherical",
            enable_plotting=False,
        )

        return OK.execute("grid", gridx, gridy, n_closest_points=10, backend="loop")

    def map(
        self, x: float, in_min: float, in_max: float, out_min: float, out_max: float
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

    def insert_interpolated_depth_map(
        self, bounds: MinMaxXy, grid_size, depths, varians
    ):
        # loop with index-x, index-y in depths. Varians should have the same indexes..

        self.__depth_map_repository.truncate_interpolated_depth_map()
        self.__depth_map_repository.insert_interpolated_depths(
            depths, varians, bounds, grid_size
        )

    def render_raw_depth_map(self, min_zoom, max_zoom):
        tiles = self.get_map_tiles(min_zoom, max_zoom)
        max_depth = self.get_max_depth()

        folder = os.path.join("ais_app", self.raw_tiles_folder)
        self.clear_folder(folder)
        self.render_legend(
            max_depth, os.path.join(folder, "legend.svg"), "Depth in meters"
        )

        for tile in tqdm(tiles):
            coordinates = tile["geom"]["coordinates"][0]
            # todo make use minmaxxy
            tile_n = max(coordinates, key=lambda x: x[1])[1]
            tile_s = min(coordinates, key=lambda x: x[1])[1]
            tile_e = max(coordinates, key=lambda x: x[0])[0]
            tile_w = min(coordinates, key=lambda x: x[0])[0]

            depths = self.get_within_box(tile_n, tile_s, tile_e, tile_w)

            if len(depths) == 0:
                continue

            img = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            for depth in depths:
                coordinates = depth["geom"]["coordinates"][0]
                grid_n = max(coordinates, key=lambda x: x[1])[1]
                grid_s = min(coordinates, key=lambda x: x[1])[1]
                grid_e = max(coordinates, key=lambda x: x[0])[0]
                grid_w = min(coordinates, key=lambda x: x[0])[0]

                # remove offset
                # n-s is reversed, as increase in pixel, is moving down,
                # while increase in latitude is moving up.
                grid_g_n = self.map(grid_n, tile_s, tile_n, 255, 0)
                grid_g_s = self.map(grid_s, tile_s, tile_n, 255, 0)
                grid_g_e = self.map(grid_e, tile_w, tile_e, 0, 255)
                grid_g_w = self.map(grid_w, tile_w, tile_e, 0, 255)

                min_depth = depth["depth"]
                min_depth_color = int(self.map(min_depth, 0, max_depth, 0, 255))
                color = (min_depth_color, 0, 255 - min_depth_color)

                draw.rectangle([(grid_g_w, grid_g_s), (grid_g_e, grid_g_n)], fill=color)

                # debug
                draw.text(
                    (128, 128), f"{tile['z']}-{tile['x']}-{tile['y']}", fill=(0, 0, 0)
                )

            img.save(os.path.join(folder, f"{tile['z']}-{tile['x']}-{tile['y']}.png"))

    def render_interpolated_depth_map(self, min_zoom, max_zoom):
        tiles = self.get_map_tiles(min_zoom, max_zoom)
        max_depth = self.get_max_depth_interpolated()

        folder = os.path.join("ais_app", self.raw_tiles_folder)
        self.clear_folder(folder)

        self.render_legend(
            max_depth, os.path.join(folder, "legend.svg"), "Depth in meters"
        )

        for tile in tqdm(tiles):
            coordinates = tile["geom"]["coordinates"][0]
            tile_bounds = MinMaxXy.from_coords(coordinates)

            depths = self.get_within_box_interpolated(tile_bounds)

            if len(depths) == 0:
                continue

            img = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            for depth in depths:
                coordinates = depth["geom"]["coordinates"][0]
                bounds_relative = MinMaxXy.from_coords(coordinates)

                bounds_in_image = MinMaxXy(
                    self.map(
                        bounds_relative.min_x,
                        tile_bounds.min_x,
                        tile_bounds.max_x,
                        0,
                        255,
                    ),
                    self.map(
                        bounds_relative.min_y,
                        tile_bounds.min_y,
                        tile_bounds.max_y,
                        255,
                        0,
                    ),
                    self.map(
                        bounds_relative.max_x,
                        tile_bounds.min_x,
                        tile_bounds.max_x,
                        0,
                        255,
                    ),
                    self.map(
                        bounds_relative.max_y,
                        tile_bounds.min_y,
                        tile_bounds.max_y,
                        255,
                        0,
                    ),
                )

                min_depth = depth["depth"]
                min_depth_color = int(self.map(min_depth, 0, max_depth, 0, 255))
                color = (min_depth_color, 0, 255 - min_depth_color)

                draw.rectangle(
                    [
                        (bounds_in_image.min_x, bounds_in_image.min_y),
                        (bounds_in_image.max_x, bounds_in_image.max_y),
                    ],
                    fill=color,
                )

                font = ImageFont.truetype(
                    "arial.ttf",
                    int((bounds_in_image.max_x - bounds_in_image.min_x) / 2),
                )
                if tile["z"] >= 11:
                    draw.text(
                        (
                            (bounds_in_image.max_x + bounds_in_image.min_x) / 2,
                            (bounds_in_image.max_y + bounds_in_image.min_y) / 2,
                        ),
                        text=f"{round(depth['depth'],1)}\n{round(depth['varians'],1)}",
                        fill="white",
                        font=font,
                    )

            img.save(f"{folder}/{tile['z']}-{tile['x']}-{tile['y']}.png")

        return "Server go brbrbr"

    def get_within_box_interpolated(self, tile_bounds):
        return self.__depth_map_repository.get_within_box_interpolated(tile_bounds)

    def render_legend(self, max: float, destination: str, description: str, min=0):
        # make custom cmap
        # https://matplotlib.org/stable/tutorials/colors/colorbar_only.html
        N = 256
        vals = np.ones((N, 4))
        vals[:, 0] = np.linspace(0, 1, N)
        vals[:, 1] = np.linspace(0, 0, N)
        vals[:, 2] = np.linspace(1, 0, N)
        from matplotlib.colors import ListedColormap

        newcmp = ListedColormap(vals)

        a = np.array([[min, max]])
        pl.figure(figsize=(9, 1.5))
        img = pl.imshow(a, cmap=newcmp)
        pl.gca().set_visible(False)
        cax = pl.axes([0.02, 0.8, 0.96, 0.1])
        pl.colorbar(orientation="horizontal", cax=cax, label=description)
        pl.savefig(destination)

    @staticmethod
    def clear_folder(folder):
        if not os.path.exists(folder):
            os.makedirs("my_folder")
        else:
            for root, dirs, files in os.walk(folder):
                for file in files:
                    os.remove(os.path.join(root, file))

    def generate_raw_depth_map(self):
        self.__depth_map_repository.generate_raw_depth_map()

    def get_max_depth_interpolated(self):
        return self.__depth_map_repository.get_max_depth_interpolated()
