from PIL import Image
from theia.utils import FileUtils


class ResizeImage():
    @classmethod
    def apply(cls, filename, bundle):
        stage = bundle.current_stage
        new_filename = FileUtils.version_filename(filename, stage.sort_order)
        im = Image.open(filename)
        size = stage.config['width'], stage.config['height']

        im.thumbnail(size, Image.ANTIALIAS)
        im.save(new_filename)
