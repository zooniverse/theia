from PIL import Image
from libtiff import TIFF, libtiff_ctypes

from theia.adapters import adapters
from theia.utils import FileUtils


class RemapImage():
    @classmethod
    def apply(cls, filenames, bundle):
        libtiff_ctypes.suppress_warnings()
        request = bundle.imagery_request
        stage = bundle.current_stage
        for filename in filenames:
            cls.do_apply(request.adapter_name, filename, stage.sort_order)

    @classmethod
    def do_apply(cls, adapter_name, filename, version_number):
        # https://stackoverflow.com/questions/50761021/how-to-open-a-tif-cmyk-16-bit-image-file
        # 'Using libtiff instead of GDAL'
        adapter = adapters[adapter_name]

        input = TIFF.open(filename).read_image()
        remapped = adapter.remap_pixel(input)
        im = Image.fromarray(remapped)
        im.convert('L')

        new_filename = FileUtils.version_filename(filename, version_number)
        im.save(new_filename)
