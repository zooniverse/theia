import csv
from ..abstract_operation import AbstractOperation
# https://docs.python.org/3/library/csv.html


class ComputeCorners(AbstractOperation):
    def compute_corner_coords(self, pixels):
        pass

    def compute_corner_pixels(self, xth, yth):
        return {
            'top_left': (xth * self.stagger, yth * self.stagger),
            'bottom_right': (xth * self.stagger + self.tile_size, yth * self.stagger + self.tile_size)
        }

    @property
    def left_edge(self):
        pass

    @property
    def right_edge(self):
        pass

    @property
    def top_edge(self):
        pass

    @property
    def bottom_edge(self):
        pass

    @property
    def scene_width(self):
        pass

    @property
    def scene_height(self):
        pass

    @property
    def output_filename(self):
        return self.config['output_filename']

    @property
    def tiled_image_filename(self):
        return self.config['tiled_image_filename']

    @property
    def stagger(self):
        return self.tile_size - self.tile_overlap

    @property
    def tile_size(self):
        return self.config['tile_size']

    @property
    def tile_overlap(self):
        return self.config['tile_overlap']
