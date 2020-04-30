import logging
from os import path
from subprocess import check_output, call

def get_dimensions(a_file):
    result = check_output([
        "convert",
        "-quiet",
        a_file,
        "-ping",
        "-format",
        '%[fx:w] %[fx:h]',
        "info:"
    ]).decode().split(' ')

    return [int(result[0].strip()), int(result[1].strip())]

def get_height(a_file):
    return int(check_output([
        "convert",
        "-quiet",
        a_file,
        "-ping",
        "-format",
        '%[fx:h]',
        "info:"
    ]).strip())

def get_width(a_file):
    return int(check_output([
        "convert",
        "-quiet",
        a_file,
        "-ping",
        "-format",
        '%[fx:w]',
        "info:"
    ]).strip())

def generate_rectangles(tiles, width, grid_size):
    rects = []
    per_row = width // grid_size + 1

    for elem in tiles:
        idx = int(elem.split("_")[1].split(".")[0])
        row = idx // per_row
        col = idx % per_row

        rects.append("-draw")
        rects.append("rectangle " +
                     str(grid_size*col) + "," +
                     str(grid_size*row)  + "  " +
                     str(grid_size*(col+1)) + "," +
                     str(grid_size*(row+1)))

    return rects

def build_mask_files(config, which_lut, which_mask):
    call([
        "convert",
        "-quiet",
        "-type",
        "GrayScale",
        "-clut",
        config.NEW_MASK,
        which_lut,
        "-clamp",
        which_mask
    ])
    return

def prepare_land_mask(config):
    call([
        "convert",
        "-quiet",
        "-type",
        "GrayScale",
        config.WATER_MASK,
        config.CLOUD_MASK,
        "-compose",
        "add",
        "-composite",
        config.SNOW_MASK,
        "-compose",
        "minus_src",
        "-composite",
        "-blur",
        config.MASK_BLUR,
        "-crop",
        str(config.GRID_SIZE)+"x"+str(config.GRID_SIZE),
        path.join(config.SCRATCH_PATH, "land", "tile_%04d.png")
    ])

def prepare_cloud_mask(config):
    call([
        "convert",
        "-quiet",
        "-type",
        "GrayScale",
        config.CLOUD_MASK,
        "-blur",
        config.MASK_BLUR,
        "-crop",
        str(config.GRID_SIZE)+"x"+str(config.GRID_SIZE),
        path.join(config.SCRATCH_PATH, "cloud", "tile_%04d.png")
    ])

def get_image_statistics(image):
    return [elem.strip() for elem in check_output([
        "convert",
        "-quiet",
        image,
        "-format",
        "\"%[fx:100*minima] %[fx:100*maxima] %[fx:100*mean] %[fx:100*standard_deviation]\"",
        "info:"
    ]).decode().strip('"').split(" ")]

def draw_visualization(land, clouds, water, config):
    args = \
        ["convert", "-quiet", config.INPUT_FILE, "-strokewidth", "0"] \
        + ["-fill", "rgba(0,255,0,0.5)"] \
        + land \
        + ["-fill", "rgba(255,255,255,0.5)"] \
        + clouds \
        + ["-fill", "rgba(0,0,255,0.5)"] \
        + water \
        + ["-alpha", "remove"] \
        + ["-resize", "1000x1000", config.SCENE_NAME + "_tiles/visualize.png"]

    call(args)

def clamp_image(source, dest, config, brighten):
    logger = logging.getLogger(config.SCENE_NAME)
    logger.info("Clamping file %s", path.basename(source))
    target = path.join(config.SCRATCH_PATH, dest  + ".png")
    _clamp_image(source, target, config, False, brighten)

def boost_image(source, config):
    logger = logging.getLogger(config.SCENE_NAME)
    logger.info("Boosting file %s", path.basename(source))
    _clamp_image(source, path.join(config.SCRATCH_PATH, "boost.png"), config, True, False)

def _clamp_image(source, dest, config, boost, brighten):
    lut = ("clamp_lut.pgm" if boost else "boost_lut.pgm")

    new_args = [
        "convert",
        "-quiet",
        "-type",
        "GrayScale",
        "-depth",
        "16",
        "-clut",
        source,
        lut,
        "-dither",
        "None",
        "-colors",
        "256",
        "-depth",
        "8",
        "-clamp",
        path.join(config.SCRATCH_PATH, "snow_mask.png"),
        "-compose",
        "lighten",
        "-composite",
    ]

    if brighten:
        new_args.extend(["-brightness-contrast", "10"])
    new_args.extend([dest])
    call(new_args)

def assemble_image(config):
    logger = logging.getLogger(config.SCENE_NAME)

    red = config.RED_CHANNEL
    green = config.GREEN_CHANNEL
    blue = config.BLUE_CHANNEL

    logger.info("Generating simplified land/water masks")

    water_mask_args = [
        "convert",
        "-quiet",
        "-type",
        "GrayScale",
        config.WATER_MASK,
        "-blur",
        "5x2",
        "-white-threshold",
        "254",
        "-blur",
        "20x2",
        "-threshold",
        "254",
        path.join(config.SCRATCH_PATH, "water.png")
    ]

    land_mask_args = [
        "convert",
        "-quiet",
        "-type",
        "GrayScale",
        path.join(config.SCRATCH_PATH, "water.png"),
        "-negate",
        path.join(config.SCRATCH_PATH, "land.png")
    ]
    call(water_mask_args)
    call(land_mask_args)

    mask_boost_args = [
        "convert",
        "-quiet",
        "-type",
        "GrayScale",
        config.INFRARED_CHANNEL,
        path.join(config.SCRATCH_PATH, "water.png"),
        "-compose",
        "darken",
        "-composite",
        path.join(config.SCRATCH_PATH, "masked.png")
    ]
    logger.info("Masking boosted green channel")
    call(mask_boost_args)

    build_green_args = [
        "convert",
        "-quiet",
        "-type",
        "GrayScale",
        green,
        path.join(config.SCRATCH_PATH, "land.png"),
        "-compose",
        "darken",
        "-composite",
        path.join(config.SCRATCH_PATH, "masked.png"),
        "-compose",
        "add",
        "-composite",
        path.join(config.SCRATCH_PATH, "green_final.png")
    ]
    logger.info("Building final green channel")
    call(build_green_args)

    assemble_args = [
        "convert",
        "-quiet",
        red,
        path.join(config.SCRATCH_PATH, "green_final.png"),
        blue,
        "-set",
        "colorspace",
        "sRGB",
        "-depth",
        "8",
        "-combine",
        path.join(config.SCRATCH_PATH, "render.png")
    ]

    logger.info("Compositing red, green, and blue images")
    call(assemble_args)
    call([
        "cp",
        path.join(config.SCRATCH_PATH, "render.png"),
        config.SCENE_NAME + "_tiles/render.png"
    ])

def prepare_tiles(config):
    call([
        "convert",
        "-quiet",
        path.join(config.SCRATCH_PATH, "render.png"),
        "-crop",
        str(config.GRID_SIZE)+"x"+str(config.GRID_SIZE),
        path.join(config.SCRATCH_PATH, "scene", "tile_%04d.png")
    ])
