from PIL import Image
from theia.utils import FileUtils

class ResizeImage():
    @classmethod
    def apply(self, filename, stage):
        new_filename = FileUtils.version_filename(filename, stage.sort_order)
        with Image.open(filename) as im:
            size = stage.config['width'], stage.config['height']
            im.thumbnail(size, Image.ANTIALIAS)
            im.save(new_filename)
