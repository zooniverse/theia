from PIL import Image
from ..abstract_operation import AbstractOperation
import os


class ResizeImage(AbstractOperation):
    def apply(self, filenames):
        self.establish_output_directory()

        for filename in filenames:
            file_title = os.path.splitext(os.path.basename(filename))[0]
            dimensions = (self.config['width'], self.config['height'])
            new_filename = '%s_resized_to_%d_%d.%s' % (
                file_title,
                self.config['width'],
                self.config['height'],
                self.output_extension
            )

            im = Image.open(filename)
            im.thumbnail(dimensions, Image.LANCZOS)
            im.save(self.output_directory + "/" + new_filename)
