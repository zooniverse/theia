from theia.adapters import adapters
from PIL import Image


class ComposeImages:
    @classmethod
    def apply(cls, filenames, bundle):
        stage = bundle.current_stage
        config = stage.config
        request = bundle.imagery_request
        output_filename = adapters[request.adapter_name].resolve_image(bundle, config['filename'], absolute_resolve=True)

        redname = filenames[stage.select_images.index(config['red'])]
        channel_r = Image.open(redname).convert('L')

        greenname = filenames[stage.select_images.index(config['green'])]
        channel_g = Image.open(greenname).convert('L')

        bluename = filenames[stage.select_images.index(config['blue'])]
        channel_b = Image.open(bluename).convert('L')

        merged = Image.merge('RGB', (channel_r, channel_g, channel_b))
        merged.save(output_filename)
