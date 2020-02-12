from PIL import Image

from ..abstract_operation import AbstractOperation
from theia.adapters import adapters
from theia.utils import FileUtils


class ComposeImages(AbstractOperation):
    def apply(self, filenames):
        output_filename = self.get_new_version(self.get_new_filename(self.config['filename']))
        try:
            channels = []

            for name in filenames:
                channels.append(Image.open(name).convert('L'))

            merged = Image.merge('RGB', tuple(channels))
            merged.save(output_filename)

        except ValueError as e:
            raise ValueError("e.message " + str(filenames))
