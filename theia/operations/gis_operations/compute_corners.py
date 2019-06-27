import csv
from PIL import Image

from ..abstract_operation import AbstractOperation
# https://docs.python.org/3/library/csv.html


class ComputeCorners(AbstractOperation):
    def apply(self, filenames):
        self._width, self._height = self.get_image_dimensions(filenames[0])
        self._topleft, self._bottomright = self.get_scene_coords()

        fieldnames = ['x', 'y', 'utm_left', 'utm_top', 'utm_right', 'utm_bottom']
        with open(self.output_filename, 'w') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            self.write_all(writer)

    def write_all(self, writer):
        top = 0
        y = 0

        while(top < self.scene_height):
            left = 0
            x = 0

            while(left < self.scene_width):
                self.write_one(writer, x, y, top, left)

                x = x + 1
                left = left + self.stagger

            y = y + 1
            top = top + self.stagger

    def write_one(self, writer, x, y, top, left):
        writer.writerow({
            'x': x,
            'y': y,
            'utm_left': self.transform_x(x),
            'utm_right': self.transform_x(x + self.tile_size),
            'utm_top': self.transform_y(y),
            'utm_bottom': self.transform_y(y + self.tile_size),
        })

    def transform_x(self, x):
        xprime = min(x, self.scene_width)
        return self.x_scale * xprime + self.left_edge

    def transform_y(self, y):
        yprime = min(y, self.scene_height)
        return self.y_scale * yprime + self.top_edge

    def get_image_dimensions(self, filename):
        with Image.open(filename) as im:
            return im.size

    def get_scene_coords(self):
        return (
            [self.adapter.get_metadata('utm_left'),
                self.adapter.get_metadata('utm_top')],
            [self.adapter.get_metadata('utm_right'),
                self.adapter.get_metadata('utm_bottom')],
        )

    @property
    def left_edge(self):
        return self._topleft[0]

    @property
    def right_edge(self):
        return self._bottomright[0]

    @property
    def top_edge(self):
        return self._topleft[1]

    @property
    def bottom_edge(self):
        return self._bottomright[1]

    @property
    def x_scale(self):
        return (self.right_edge - self.left_edge) / self.scene_width

    @property
    def y_scale(self):
        return (self.bottom_edge - self.top_edge) / self.scene_height

    @property
    def scene_width(self):
        return self._width  # pragma: nocover

    @property
    def scene_height(self):
        return self._height  # pragma: nocover

    @property
    def output_filename(self):
        return self.get_new_version(self.get_new_filename(self.config['output_filename']))

    @property
    def stagger(self):
        return self.tile_size - self.tile_overlap

    @property
    def tile_size(self):
        return self.config['tile_size']

    @property
    def tile_overlap(self):
        return self.config['tile_overlap']
