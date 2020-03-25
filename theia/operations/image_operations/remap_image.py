from PIL import Image
from libtiff import TIFF

from ..abstract_operation import AbstractOperation
from theia.adapters import adapters


class RemapImage(AbstractOperation):
    def apply(self, filenames):
        self.establish_output_directory()

        for filename in filenames:
            # https://stackoverflow.com/questions/50761021/how-to-open-a-tif-cmyk-16-bit-image-file
            # 'Using libtiff instead of GDAL'
            new_filename = self.get_new_version(filename)

            input = TIFF.open(filename).read_image()
            remapped = self.adapter.remap_pixel(input)
            im = Image.fromarray(remapped)
            im.convert('L')

            im.save(self.output_directory + "/" + new_filename)
