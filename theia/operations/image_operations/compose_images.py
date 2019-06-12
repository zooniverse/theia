from theia.adapters import adapters
from PIL import Image


class ComposeImages:
    @classmethod
    def apply(cls, filenames, bundle):
        stage = bundle.current_stage
        config = stage.config
        request = bundle.imagery_request
        output_filename = adapters[request.adapter_name].resolve_image(config['filename'])

        channel_r = Image.open(filenames[stage.select_images.index(config['red'])])
        channel_g = Image.open(filenames[stage.select_images.index(config['green'])])
        channel_b = Image.open(filenames[stage.select_images.index(config['blue'])])

        merged = Image.merge('RGB', (channel_r, channel_g, channel_b))
        merged.save(output_filename)
