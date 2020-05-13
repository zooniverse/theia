from __future__ import division

from lxml import etree

import csv
import logging
import tempfile
from os import path, mkdir, listdir
from shutil import rmtree, copy
from subprocess import check_output, call

from ..abstract_operation import AbstractOperation

# https://docs.python.org/3/library/csv.html
LANDSAT = {'red': 'band5', 'green': 'band2', 'blue': 'band3', 'infrared': 'band4'}
LANDSAT8 = {'red': 'band6', 'green': 'band3', 'blue': 'band4', 'infrared': 'band5'}


ff_config = type('Config', (object,), {
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
})()

class FloatingForest(AbstractOperation):
    def apply(self, filenames):

        print("Floating forest filenames: " + str(filenames))
        self.establish_output_directory()

        run_ff(filenames, self.output_directory)

def parse_options(filenames):
    ff_config.SCENE_NAME = path.dirname(filenames[0])
    ff_config.NEW_MASK = path.join(ff_config.SCENE_DIR, ff_config.SCENE_NAME + "_pixel_qa.tif")
    ff_config.METADATA_SRC = path.join(ff_config.SCENE_DIR, ff_config.SCENE_NAME + ".xml")
    ff_config.INPUT_FILE = ff_config.NEW_MASK

#===========SIMPLE======================
logging.basicConfig(
    format='[ff-import %(name)s] %(levelname)s %(asctime)-15s %(message)s'
)

LANDSAT = {'red': 'band5', 'green': 'band2', 'blue': 'band3', 'infrared': 'band4'}
LANDSAT8 = {'red': 'band6', 'green': 'band3', 'blue': 'band4', 'infrared': 'band5'}

def usage():
    print("""
simple.py (Simple Image Pipeline)

python simple.py [--option] SCENE_DIR

This script is used to process satellite imagery from LANDSAT 4, 5, 7, and 8
into subjects for Floating Forests. This includes sorting out tiles that only
contain land or contain too many clouds, as well as compositing the different
bands together into an RGB image and boosting certain parts of the green
channel to aid in kelp-spotting.

    --full                  Run full pipeline

    --clean                 Recreate scratch directory

    --generate              Perform all scene tile generation tasks
    --assemble              Perform color adjustment and build color output
    --generate-tiles        Build color tiles of scene

    --sort-tiles            Perform all tile sorting tasks
    --generate-mask         Regenerate mask tiles
    --remove-land           Reject tiles that are only land
    --remove-clouds         Reject tiles that are too cloudy
    --remove-all            Reject tiles that are only land or too cloudy
    --reject                Sort tiles into accepted and rejected folders

    --visualize             Show which tiles would be rejected

    --manifest              Build a manifest file for Panoptes subject upload

    --grid-size=XXX         Set custom tile size

    --source-dir=MY_PATH    Load scenes from a specified directory

    --land-threshhold=XX    Configure land detection
    --land-sensitivity=XX

    --cloud-threshhold=XX   Configure cloud detection
    --cloud-sensitivity=XX
    """)

def parse_options(filenames):
    # note that logger is undefined when this method is active
    ff_config.WITHTEMPDIR = True
    ff_config.REBUILD = True
    ff_config.ASSEMBLE_IMAGE = True
    ff_config.SLICE_IMAGE = True
    ff_config.GENERATE_MASK_TILES = True
    ff_config.REMOVE_LAND = True
    ff_config.REMOVE_CLOUDS = True
    ff_config.REJECT_TILES = True
    ff_config.BUILD_MANIFEST = True
    ff_config.VISUALIZE_SORT = True

    ff_config.SCENE_DIR = path.dirname(filenames[0])
    path_components = ff_config.SCENE_DIR.split('/')
    ff_config.SCENE_NAME = path_components[len(path_components) - 1]
    ff_config.NEW_MASK = path.join(ff_config.SCENE_DIR, ff_config.SCENE_NAME + "_pixel_qa.tif")
    ff_config.METADATA_SRC = path.join(ff_config.SCENE_DIR, ff_config.SCENE_NAME + ".xml")
    ff_config.INPUT_FILE = ff_config.NEW_MASK

def generate_mask_tiles():
    logger = logging.getLogger(ff_config.SCENE_NAME)
    logger.info(
        "Generating mask tiles of " + str(ff_config.GRID_SIZE) +
        "x" + str(ff_config.GRID_SIZE) + " pixels")

    logger.info("Generating land mask tiles")
    prepare_land_mask(ff_config)

    logger.info("Generating cloud mask tiles")
    prepare_cloud_mask(ff_config)

    generated_count = len(get_files_by_extension(path.join(ff_config.SCRATCH_PATH, "land"), "png"))
    logger.info("Generated " + str(generated_count) + " tiles")

def apply_rules(candidates, rejects, subdirectory, rules):
    accum = []
    logger = logging.getLogger(ff_config.SCENE_NAME)

    logger.info("Examining " + str(len(candidates)) + " tiles for " + subdirectory)
    for filename in candidates:
        done = False
        statistics = get_image_statistics(path.join(
            ff_config.SCRATCH_PATH,
            subdirectory,
            filename))
	#debug
        for rule in rules:
            if not rule(*statistics):
                rejects.append(filename)
                done = True
                break
        if done:
            continue

        accum.append(filename)

    return accum

def index_to_location(filename, width, grid_size):
    per_row = width // grid_size + 1
    idx = int(filename.split("_")[1].split(".")[0])
    row = idx // per_row
    col = idx % per_row

    return [row, col]

def build_dict_for_csv(filename, reason, ff_config):
    [width, height] = get_dimensions(path.join(ff_config.SCRATCH_PATH, "scene", filename))
    [row, column] = index_to_location(filename, ff_config.width, ff_config.GRID_SIZE)

    my_dict = {
        '#filename': filename,
        '#reason': reason,
        '#row': row,
        '#column': column,
        '#width': width,
        '#height': height,
    }

    coordinate_metadata = compute_coordinate_metadata(row, column, width, height, ff_config)

    my_dict.update(coordinate_metadata)
    my_dict.update(ff_config.METADATA)
    return my_dict


def run_ff(filenames, output_directory):
    retained_tiles = []
    no_water = []
    too_cloudy = []

    parse_options(filenames)

    logger = logging.getLogger(ff_config.SCENE_NAME)
    logger.setLevel(logging.INFO)
    logger.info("Processing start")

    accepts = []
    rejects = []

    [ff_config.width, ff_config.height] = get_dimensions(ff_config.INPUT_FILE)

    if ff_config.REBUILD or not scratch_exists(ff_config):
        build_scratch(ff_config, output_directory)

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

    if ff_config.ASSEMBLE_IMAGE:
        logger.info("Processing source data to remove negative pixels")
        clamp = clamp_image
        boost = boost_image
        clamp(ff_config.RED_CHANNEL, "red", ff_config, False)
        clamp(ff_config.INFRARED_CHANNEL, "green", ff_config, False)
        clamp(ff_config.BLUE_CHANNEL, "blue", ff_config, True)

        # red_output = path.join(ff_config.SCRATCH_PATH, "red.png")
        # green_output = path.join(ff_config.SCRATCH_PATH, "green.png")
        # blue_output = path.join(ff_config.SCRATCH_PATH, "blue.png")
        #
        # red_image = Image.open(ff_config.RED_CHANNEL).convert('L')
        # red_enhanced = ImageEnhance.Contrast(red_image)
        # red_enhanced.enhance(0.5).save(red_output)
        #
        # green_image = Image.open(ff_config.GREEN_CHANNEL).convert('L')
        # green_enhanced = ImageEnhance.Contrast(green_image)
        # green_enhanced.enhance(0.5).save(green_output)
        #
        # blue_image = Image.open(ff_config.BLUE_CHANNEL).convert('L')
        # blue_enhanced = ImageEnhance.Contrast(blue_image)
        # blue_enhanced.enhance(0.5).save(blue_output)

        boost(ff_config.INFRARED_CHANNEL, ff_config)
        ff_config.RED_CHANNEL = path.join(ff_config.SCRATCH_PATH, "red.png")
        ff_config.GREEN_CHANNEL = path.join(ff_config.SCRATCH_PATH, "green.png")
        ff_config.BLUE_CHANNEL = path.join(ff_config.SCRATCH_PATH, "blue.png")
        ff_config.INFRARED_CHANNEL = path.join(ff_config.SCRATCH_PATH, "boost.png")
        assemble_image(ff_config)
    else:
        logger.info("Skipping scene generation")

    if ff_config.SLICE_IMAGE:
        logger.info(
            "Generating scene tiles of " +
            str(ff_config.GRID_SIZE) + "x" +
            str(ff_config.GRID_SIZE)+" pixels")
        prepare_tiles(ff_config)
    else:
        logger.info("Skipping scene tile generation")

    if ff_config.GENERATE_MASK_TILES:
        generate_mask_tiles()
    else:
        logger.info("Skipping mask generation")

    if ff_config.REJECT_TILES or ff_config.VISUALIZE_SORT:

        retained_tiles = get_files_by_extension(path.join(ff_config.SCRATCH_PATH, "land"), "png")

        if ff_config.REMOVE_CLOUDS:
            retained_tiles = apply_rules(
                retained_tiles, too_cloudy, "cloud", [
                    lambda imin, imax, imean, idev: float(imin) < ff_config.CLOUD_THRESHHOLD,
                    lambda imin, imax, imean, idev: (
                        float(imean) < ff_config.CLOUD_THRESHHOLD or
                        float(idev) > ff_config.CLOUD_SENSITIVITY
                    )
                ])
        else:
            logger.info("Skipping cloud removal")

        if ff_config.REMOVE_LAND:
            retained_tiles = apply_rules(
                retained_tiles, no_water, "land", [
                    lambda imin, imax, imean, idev: float(imax) > ff_config.LAND_THRESHHOLD,
                    lambda imin, imax, imean, idev: (
                        float(imean) > ff_config.LAND_THRESHHOLD or
                        float(idev) > ff_config.LAND_SENSITIVITY
                    )
                ])
        else:
            logger.info("Skipping land removal")


    if ff_config.VISUALIZE_SORT:
        logger.info(str(len(retained_tiles))+" tiles retained")
        logger.info(str(len(no_water))+" tiles without water rejected")
        logger.info(str(len(too_cloudy))+" tiles rejected for clouds")

        logger.info("Generating tile visualization")
        land = generate_rectangles(no_water, ff_config.width, ff_config.GRID_SIZE)
        clouds = generate_rectangles(too_cloudy, ff_config.width, ff_config.GRID_SIZE)
        water = generate_rectangles(retained_tiles, ff_config.width, ff_config.GRID_SIZE)
        draw_visualization(land, clouds, water, ff_config)

    if ff_config.REJECT_TILES:
        logger.info("Copying accepted tiles")
        for filename in retained_tiles:
            accept_tile(filename, ff_config)
            accepts.append(build_dict_for_csv(filename, "Accepted", ff_config))

        logger.info("Copying rejected tiles")
        for filename in no_water:
            reject_tile(filename, ff_config)
            rejects.append(build_dict_for_csv(filename, "No Water", ff_config))

        for filename in too_cloudy:
            reject_tile(filename, ff_config)
            rejects.append(build_dict_for_csv(filename, "Too Cloudy", ff_config))

        logger.info("Writing csv file")
        rejects = sorted(rejects, key=lambda k: k['#filename'])
        write_rejects(
            path.join("{0}_tiles".format(ff_config.SCENE_NAME), "rejected", "rejected.csv"),
            rejects)

    if ff_config.BUILD_MANIFEST:
        logger.info("Writing manifest")
        write_manifest(
            path.join("{0}_tiles".format(ff_config.SCENE_NAME), "accepted", "manifest.csv"),
            accepts)

    maybe_clean_scratch(ff_config)

    logger.info("Processing finished")

#=========FILE OPERATIONS=============================

def find_scene_name(config):
    files = get_files_by_extension(config.SCENE_DIR, "xml")
    return path.splitext(files[0])[0]

def accept_tile(filename, config):
    copy(
        path.join(config.SCRATCH_PATH, "scene", filename),
        path.join("{0}_tiles".format(config.SCENE_NAME), "accepted", filename)
    )

def reject_tile(filename, config):
    copy(
        path.join(config.SCRATCH_PATH, "scene", filename),
        path.join("{0}_tiles".format(config.SCENE_NAME), "rejected", filename)
    )

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

def scratch_exists(config):
    return path.exists(config.SCRATCH_PATH)

def build_scratch(config, output_directory):
    logger = logging.getLogger(config.SCENE_NAME)

    should_use_tempdir = config.WITHTEMPDIR

    if should_use_tempdir:
        config.SCRATCH_PATH = output_directory
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

def get_files_by_extension(filepath, extension):
    accum = []

    files = listdir(filepath)

    for filename in files:
        if filename.endswith(extension):
            accum.append(filename)

    return accum

def maybe_clean_scratch(config):
    logger = logging.getLogger(config.SCENE_NAME)
    # if config.WITHTEMPDIR:
    #     logger.info("attempting to clean up scratch directory")
        # rmtree(config.SCRATCH_PATH)

#=========XML OPERATIONS=============================

def get_field_text(tree, path):
    nsmap = {"espa": tree.getroot().nsmap[None]}
    node = tree.xpath(path, namespaces=nsmap)
    if len(node) > 0:
        return node[0].text
    return ''

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

#========GIS OPERATIONS==================

def compute_lat_lon(x, y, utm_zone):
    # p = Proj(proj='utm', zone=utm_zone, ellps='WGS84')
    # lat, lon = p(x, y, inverse=True)
    # return [lat, lon]
    return [x, y]

def compute_tile_coords(row, col, width, height, config):
    scene_top = float(config.METADATA["#scene_corner_UL_y"])
    scene_bottom = float(config.METADATA["#scene_corner_LR_y"])
    scene_left = float(config.METADATA["#scene_corner_UL_x"])
    scene_right = float(config.METADATA["#scene_corner_LR_x"])

    scene_span_x = scene_right - scene_left
    scene_span_y = scene_bottom - scene_top

    left = scene_left + ((col * config.GRID_SIZE) / config.width) * scene_span_x
    top = scene_top + ((row * config.GRID_SIZE) / config.height) * scene_span_y
    right = left + (width / config.width) * scene_span_x
    bottom = top + (height / config.height) * scene_span_y

    return [left, top, right, bottom]

def compute_coordinate_metadata(row, col, width, height, config):
    [left, top, right, bottom] = compute_tile_coords(row, col, width, height, config)
    tile_center_x = (left+right)/2
    tile_center_y = (top+bottom)/2

    [lon, lat] = compute_lat_lon(tile_center_x, tile_center_y, config.METADATA['#utm_zone'])

    return {
        '#tile_UL_x': left,
        '#tile_UL_y': top,
        '#tile_UR_x': right,
        '#tile_UR_y': top,
        '#tile_LL_x': left,
        '#tile_LL_y': bottom,
        '#tile_LR_x': right,
        '#tile_LR_y': bottom,

        '#tile_center_x': tile_center_x,
        '#tile_center_y': tile_center_y,

        'center_lat': lat,
        'center_lon': lon,
        'map_link': generate_map_link(lat, lon)
    }


def generate_map_link(lat, lon):
    return "http://maps.google.com/maps?q={0}+{1}&ll={0},{1}&t=k&z=12".format(lat, lon)

#============CSV OPERATIONS============


def write_manifest(csv_filename, accepted):
    if not accepted or len(accepted) < 1:
        return

    with open(csv_filename, 'w') as csvfile:

        fieldnames = ['#filename', '#row', '#column']

        for key in sorted(accepted[0].keys()):
            if key == "#reason":
                continue

            if not key in fieldnames:
                fieldnames.append(key)

        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, extrasaction='ignore')

        writer.writeheader()

        for subject in accepted:
            writer.writerow(subject)


def write_rejects(csv_filename, rejects):
    if not rejects or len(rejects) < 1:
        return

    with open(csv_filename, 'w') as csvfile:

        fieldnames = ['#filename', '#reason', '#row', '#column']
        for key in sorted(rejects[0].keys()):
            if not key in fieldnames:
                fieldnames.append(key)

        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, extrasaction='ignore')

        writer.writeheader()

        for reject in rejects:
            writer.writerow(reject)
