from PIL import Image
from libtiff import TIFF

from ..abstract_operation import AbstractOperation
from theia.adapters import adapters


class RemapImage(AbstractOperation):
    def apply(self, filenames):
        for filename in filenames:
            # https://stackoverflow.com/questions/50761021/how-to-open-a-tif-cmyk-16-bit-image-file
            # 'Using libtiff instead of GDAL'
            input = TIFF.open(filename).read_image()
            remapped = self.adapter.remap_pixel(input)
            im = Image.fromarray(remapped)
            im.convert('L')

            new_filename = self.get_new_version(filename)
            im.save(new_filename)
