import csv
from PIL import Image

from ..abstract_operation import AbstractOperation
from os import path
import logging

from os import path, mkdir, listdir
from shutil import rmtree, copy
import tempfile
from lxml import etree
from subprocess import check_output, call



# https://docs.python.org/3/library/csv.html
LANDSAT = {'red': 'band5', 'green': 'band2', 'blue': 'band3', 'infrared': 'band4'}
LANDSAT8 = {'red': 'band6', 'green': 'band3', 'blue': 'band4', 'infrared': 'band5'}


ff_config = {
    'GRID_SIZE': 350,
    'MASK_BLUR': "0x10",
    'SCRATCH_PATH': "scratch",
    'LAND_THRESHHOLD': 3,
    'LAND_SENSITIVITY': 5,
    'CLOUD_THRESHHOLD': 10,
    'CLOUD_SENSITIVITY': 80,

    'EROS_USERNAME': 'zooniverse-test',
    'EROS_PASSWORD': 'PASSWORD',

    'SCENE': '',
    'GENERATE_MASK_TILES': False,
    'REJECT_TILES': False,
    'VISUALIZE_SORT': False,
    'REMOVE_LAND': False,
    'REMOVE_CLOUDS': False,
    'REMOVE_NEGATIVE': False,
    'ASSEMBLE_IMAGE': False,
    'SLICE_IMAGE': False,
    'REBUILD': False,
    'BUILD_MANIFEST': False,

    'WITHTEMPDIR': False,

    'width': 0
}

class FloatingForest(AbstractOperation):
    def apply(self, filenames):
        print("Floating forest filenames: " + filenames)
        self.establish_output_directory()

        retained_tiles = []
        no_water = []
        too_cloudy = []

        parse_options(filenames)

        logger = logging.getLogger(ff_config.SCENE_NAME)
        logger.setLevel(logging.INFO)
        logger.info("Processing start")

        accepts = []
        rejects = []

        [ff_config.width, ff_config.height] = img.get_dimensions(ff_config.INPUT_FILE)

        if ff_config.REBUILD or not scratch_exists(ff_config):
            build_scratch(ff_config)

        logger.info("Building scene tile output directory")
        build_output(ff_config.SCENE_NAME)

        ff_config.SATELLITE = LANDSAT
        metadata = parse_metadata(ff_config.SCENE_DIR, ff_config.METADATA_SRC)
        ff_config.METADATA = metadata
        if ff_config.METADATA['spacecraft'] == 'LANDSAT_8':
            ff_config.SATELLITE = LANDSAT8

        ff_config.RED_CHANNEL = path.join(
            ff_config.SCENE_DIR, ff_config.SCENE_NAME + "_sr_" + ff_config.SATELLITE['red'] + ".tif")
        ff_config.GREEN_CHANNEL = path.join(
            ff_config.SCENE_DIR, ff_config.SCENE_NAME + "_sr_" + ff_config.SATELLITE['green'] + ".tif")
        ff_config.BLUE_CHANNEL = path.join(
            ff_config.SCENE_DIR, ff_config.SCENE_NAME + "_sr_" + ff_config.SATELLITE['blue'] + ".tif")
        ff_config.INFRARED_CHANNEL = path.join(
            ff_config.SCENE_DIR, ff_config.SCENE_NAME + "_sr_" + ff_config.SATELLITE['infrared'] + ".tif")

        logger.info("Building water mask")
        ff_config.WATER_MASK = path.join(ff_config.SCRATCH_PATH, "water_mask.png")
        build_mask_files(ff_config, "water_lut.pgm", ff_config.WATER_MASK)
        logger.info("Building cloud mask")
        ff_config.CLOUD_MASK = path.join(ff_config.SCRATCH_PATH, "cloud_mask.png")
        build_mask_files(ff_config, "cloud_lut.pgm", ff_config.CLOUD_MASK)
        logger.info("Building snow mask")
        ff_config.SNOW_MASK = path.join(ff_config.SCRATCH_PATH, "snow_mask.png")
        build_mask_files(ff_config, "snow_lut.pgm", ff_config.SNOW_MASK)
        ff_config.INPUT_FILE = ff_config.WATER_MASK


def parse_options(filenames):
    ff_config.SCENE_NAME = path.dirname(filenames[0])
    ff_config.NEW_MASK = path.join(ff_config.SCENE_DIR, ff_config.SCENE_NAME + "_pixel_qa.tif")
    ff_config.METADATA_SRC = path.join(ff_config.SCENE_DIR, ff_config.SCENE_NAME + ".xml")
    ff_config.INPUT_FILE = ff_config.NEW_MASK

#=========FILE OPERATIONS=============================

def build_output(scene_name):
    logger = logging.getLogger(scene_name)
    target = "{0}_tiles".format(scene_name)

    if path.exists(target):
        logger.info("Removing existing output tiles")
        rmtree(target)

    logger.info("Building output subdirectories")
    mkdir(target)
    mkdir(path.join(target, "accepted"))
    mkdir(path.join(target, "rejected"))

def build_scratch(config):
    logger = logging.getLogger(config.SCENE_NAME)

    should_use_tempdir = config.WITHTEMPDIR

    if should_use_tempdir:
        config.SCRATCH_PATH = tempfile.mkdtemp(prefix='ff-import-')
        logger.info("Using true scratch directory {0}".format(config.SCRATCH_PATH))

    scratch_path = config.SCRATCH_PATH
    if not config.WITHTEMPDIR and path.exists(scratch_path):
        logger.info("Removing existing scratch tiles")
        rmtree(scratch_path)

    if not config.WITHTEMPDIR:
        mkdir(scratch_path)

    logger.info("Building scratch tile directories")
    mkdir(path.join(scratch_path, "land"))
    mkdir(path.join(scratch_path, "cloud"))
    mkdir(path.join(scratch_path, "scene"))

def scratch_exists(config):
    return path.exists(config.SCRATCH_PATH)

#=========XML OPERATIONS=============================

def parse_metadata(scene, xml_filename):
    logger = logging.getLogger(scene)
    logger.info("Parsing XML metadata from {0}".format(xml_filename))

    result = {'!scene': scene}

    tree = etree.parse(xml_filename)
    nsmap = {"espa": tree.getroot().nsmap[None]}

    result['acquired_date'] = get_field_text(tree, "espa:global_metadata/espa:acquisition_date")
    result['acquired_time'] = get_field_text(tree, "espa:global_metadata/espa:scene_center_time")
    result['sensor_id'] = get_field_text(tree, "espa:global_metadata/espa:instrument")
    result['spacecraft'] = get_field_text(tree, 'espa:global_metadata/espa:satellite')

    result['!earth_sun_distance'] = get_field_text(
        tree,
        "espa:global_metadata/espa:earth_sun_distance")

    angles = tree.xpath("espa:global_metadata/espa:solar_angles", namespaces=nsmap)
    if len(angles) > 0:
        result['!sun_azimuth'] = angles[0].get("azimuth")
        result['!sun_zenith'] = angles[0].get("zenith")

    covers = tree.xpath(
        "espa:bands/espa:band[@name='cfmask']/espa:percent_coverage/espa:cover",
        namespaces=nsmap)
    for cover in covers:
        if cover.get("type") == "cloud":
            result['!cloud_cover'] = cover.text
        if cover.get("type") == "water":
            result['!water_cover'] = cover.text

    result['#utm_zone'] = get_field_text(
        tree,
        "espa:global_metadata/espa:projection_information/espa:utm_proj_params/espa:zone_code")

    corners = tree.xpath(
        "espa:global_metadata/espa:projection_information/espa:corner_point",
        namespaces=nsmap)
    for corner in corners:
        result["#scene_corner_{0}_x".format(corner.get("location"))] = corner.get("x")
        result["#scene_corner_{0}_y".format(corner.get("location"))] = corner.get("y")

    return result

def get_field_text(tree, path):
    nsmap = {"espa": tree.getroot().nsmap[None]}
    node = tree.xpath(path, namespaces=nsmap)
    if len(node) > 0:
        return node[0].text
    return ''

#=========IMAGE OPERATIONS=============================

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





