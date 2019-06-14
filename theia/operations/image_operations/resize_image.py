from PIL import Image

from ..abstract_operation import AbstractOperation
from theia.utils import FileUtils


class ResizeImage(AbstractOperation):
    def apply(self, filenames):
        for filename in filenames:
            new_filename = self.get_new_version(filename)
            dimensions = (self.config['width'], self.config['height'],)

            im = Image.open(filename)
            im.thumbnail(dimensions, Image.ANTIALIAS)
            im.save(new_filename)
