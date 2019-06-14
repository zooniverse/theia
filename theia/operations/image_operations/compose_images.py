from PIL import Image

from theia.adapters import adapters
from theia.utils import FileUtils


class ComposeImages:
    @classmethod
    def apply(cls, filenames, bundle):
        stage = bundle.current_stage
        config = stage.config
        request = bundle.imagery_request
        adapter = adapters[request.adapter_name]
        relative_name = adapter.resolve_relative_image(bundle, config['filename'])
        output_filename = FileUtils.absolutize(bundle=bundle, filename=relative_name)

        redname = filenames[stage.select_images.index(config['red'])]
        channel_r = Image.open(redname).convert('L')

        greenname = filenames[stage.select_images.index(config['green'])]
        channel_g = Image.open(greenname).convert('L')

        bluename = filenames[stage.select_images.index(config['blue'])]
        channel_b = Image.open(bluename).convert('L')

        merged = Image.merge('RGB', (channel_r, channel_g, channel_b))
        merged.save(output_filename)
