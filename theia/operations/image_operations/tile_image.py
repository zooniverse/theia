from PIL import Image
import numpy as np
import os
import os.path
from ..abstract_operation import AbstractOperation
from theia.utils import FileUtils


class TileImage(AbstractOperation):
    def apply(self, filenames):
        self.establish_output_directory()
        for filename in filenames:
            self.tile_one(filename)

    def tile_one(self, filename):
        (path, file_only) = os.path.split(filename)
        file_only = os.path.splitext(file_only)[0]
        with Image.open(filename) as im:
            pixels = np.asarray(im)

            top = 0
            y = 0

            while(top < (im.height)):
                self.build_row(file_only, top, y, pixels, im.width)

                y = y + 1
                top = top + self.stagger

    def construct_tile_name(self, file, x, y):
        return '%s/%s_tile_%03d_%03d.%s' % (
            self.output_directory,
            file,
            y,
            x,
            'png'
        )

    def build_row(self, filename, top, y, pixels, width):
        left = 0
        x = 0
        while(left < width):
            tile_name = self.construct_tile_name(filename, x, y)
            self.build_tile(pixels, top, left, tile_name)

            x = x + 1
            left = left + self.stagger

    def build_tile(self, pixels, top, left, filename):
        bottom = top + self.tile_size
        right = left + self.tile_size
        slice = pixels[top:bottom, left:right]

        with Image.fromarray(slice) as tile:
            tile.save(filename, 'png')

    @property
    def stagger(self):
        return self.tile_size - self.tile_overlap

    @property
    def tile_size(self):
        return self.config['tile_size']

    @property
    def tile_overlap(self):
        return self.config['tile_overlap']