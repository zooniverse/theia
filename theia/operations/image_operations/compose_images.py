from PIL import Image

from ..abstract_operation import AbstractOperation
from theia.adapters import adapters
from theia.utils import FileUtils


class ComposeImages(AbstractOperation):
    def apply(self, filenames):
        self.establish_output_directory()

        output_filename = self.get_new_version(f"{self.config['filename']}.{self.output_extension}")

        try:
            channels = []

            for name in filenames:
                channels.append(Image.open(name).convert('L'))

            merged = Image.merge('RGB', tuple(channels))

            merged.save(self.output_directory + "/" + output_filename)

        except ValueError as e:
            raise ValueError("e.message " + str(filenames))
