from PIL import Image

from ..abstract_operation import AbstractOperation
from theia.adapters import adapters
from theia.utils import FileUtils


class ComposeImages(AbstractOperation):
    def apply(self, filenames):
        output_filename = self.get_new_version(self.get_new_filename(self.config['filename']))

        redname = filenames[self.select_images.index(self.config['red'])]
        greenname = filenames[self.select_images.index(self.config['green'])]
        bluename = filenames[self.select_images.index(self.config['blue'])]

        channel_r = Image.open(redname).convert('L')
        channel_g = Image.open(greenname).convert('L')
        channel_b = Image.open(bluename).convert('L')

        merged = Image.merge('RGB', (channel_r, channel_g, channel_b))
        merged.save(output_filename)
