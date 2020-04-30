from os import path
from sys import argv
import logging

from PIL import Image, ImageEnhance


import image_operations as img
from csv_operations import write_rejects, write_manifest

from file_operations import (
    build_output, scratch_exists,
    build_scratch, get_files_by_extension, accept_tile, reject_tile,
    maybe_clean_scratch, find_scene_name)
from gis_operations import compute_coordinate_metadata
from xml_operations import parse_metadata
from ff_config import ff_config

logging.basicConfig(
    format='[ff-import %(name)s] %(levelname)s %(asctime)-15s %(message)s'
)

LANDSAT = {'red': 'band5', 'green': 'band2', 'blue': 'band3', 'infrared': 'band4'}
LANDSAT8 = {'red': 'band6', 'green': 'band3', 'blue': 'band4', 'infrared': 'band5'}

def usage():
    print """
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
    """


def parse_options(filenames):
    # note that logger is undefined when this method is active
    for arg in argv:
        if arg == "simple.py":
            continue

        if arg == "--help" or arg == "-?":
            # do nothing, we'll fall through to usage
            () #noqa

        elif arg == "--full":
            ff_config.WITHTEMPDIR = False
            ff_config.REBUILD = True
            ff_config.ASSEMBLE_IMAGE = True
            ff_config.SLICE_IMAGE = True
            ff_config.GENERATE_MASK_TILES = True
            ff_config.REMOVE_LAND = True
            ff_config.REMOVE_CLOUDS = True
            ff_config.REJECT_TILES = True
            ff_config.BUILD_MANIFEST = True
            ff_config.VISUALIZE_SORT = True

        elif arg == "--assemble":
            ff_config.ASSEMBLE_IMAGE = True
        elif arg == "--generate-tiles":
            ff_config.SLICE_IMAGE = True
        elif arg == "--generate":
            ff_config.ASSEMBLE_IMAGE = True
            ff_config.SLICE_IMAGE = True

        elif arg == "--clean":
            ff_config.REBUILD = True

        elif arg == "--sort-tiles":
            ff_config.GENERATE_MASK_TILES = True
            ff_config.REMOVE_LAND = True
            ff_config.REMOVE_CLOUDS = True
            ff_config.REJECT_TILES = True
        elif arg == "--generate-mask":
            ff_config.GENERATE_MASK_TILES = True
        elif arg == "--remove-land":
            ff_config.REMOVE_LAND = True
        elif arg == "--remove-clouds":
            ff_config.REMOVE_CLOUDS = True
        elif arg == "--remove-all":
            ff_config.REMOVE_CLOUDS = True
            ff_config.REMOVE_LAND = True
        elif arg == "--visualize":
            ff_config.VISUALIZE_SORT = True
        elif arg == "--reject":
            ff_config.REJECT_TILES = True
        elif arg == "--manifest":
            ff_config.BUILD_MANIFEST = True

        elif arg.startswith("--grid-size="):
            ff_config.GRID_SIZE = int(arg.split("=")[1])
        elif arg.startswith("--land-threshhold="):
            ff_config.LAND_THRESHHOLD = int(arg.split("=")[1])
        elif arg.startswith("--land-sensitivity="):
            ff_config.LAND_SENSITIVITY = int(arg.split("=")[1])
        elif arg.startswith("--cloud-threshhold="):
            ff_config.CLOUD_THRESHHOLD = int(arg.split("=")[1])
        elif arg.startswith("--cloud-sensitivity="):
            ff_config.CLOUD_SENSITIVITY = int(arg.split("=")[1])
        else:
            ff_config.SCENE_DIR = arg

    ff_config.SCENE_NAME = path.dirname(filenames[0])
    print("ZE SCENE NAME IS: " + ff_config.SCENE_NAME)
    ff_config.NEW_MASK = path.join(ff_config.SCENE_DIR, ff_config.SCENE_NAME + "_pixel_qa.tif")
    ff_config.METADATA_SRC = path.join(ff_config.SCENE_DIR, ff_config.SCENE_NAME + ".xml")
    ff_config.INPUT_FILE = ff_config.NEW_MASK

def generate_mask_tiles():
    logger = logging.getLogger(ff_config.SCENE_NAME)
    logger.info(
        "Generating mask tiles of " + str(ff_config.GRID_SIZE) +
        "x" + str(ff_config.GRID_SIZE) + " pixels")

    logger.info("Generating land mask tiles")
    img.prepare_land_mask(ff_config)

    logger.info("Generating cloud mask tiles")
    img.prepare_cloud_mask(ff_config)

    generated_count = len(get_files_by_extension(path.join(ff_config.SCRATCH_PATH, "land"), "png"))
    logger.info("Generated " + str(generated_count) + " tiles")

def apply_rules(candidates, rejects, subdirectory, rules):
    accum = []
    logger = logging.getLogger(ff_config.SCENE_NAME)

    logger.info("Examining " + str(len(candidates)) + " tiles for " + subdirectory)
    for filename in candidates:
        done = False
        statistics = img.get_image_statistics(path.join(
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
    [width, height] = img.get_dimensions(path.join(ff_config.SCRATCH_PATH, "scene", filename))
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


def main(filenames):
    retained_tiles = []
    no_water = []
    too_cloudy = []

    parse_options(filenames)

    if  (not ff_config.GENERATE_MASK_TILES and
         not ff_config.REJECT_TILES and
         not ff_config.VISUALIZE_SORT and
         not ff_config.ASSEMBLE_IMAGE and
         not ff_config.SLICE_IMAGE and
         not ff_config.BUILD_MANIFEST and
         not ff_config.REBUILD):
        usage()
        return

    if ((ff_config.GENERATE_MASK_TILES or
         ff_config.REJECT_TILES or
         ff_config.VISUALIZE_SORT or
         ff_config.ASSEMBLE_IMAGE or
         ff_config.BUILD_MANIFEST or
         ff_config.SLICE_IMAGE) and
            ff_config.SCENE_DIR == ''):
        usage()
        return

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
    img.build_mask_files(ff_config, "water_lut.pgm", ff_config.WATER_MASK)
    logger.info("Building cloud mask")
    ff_config.CLOUD_MASK = path.join(ff_config.SCRATCH_PATH, "cloud_mask.png")
    img.build_mask_files(ff_config, "cloud_lut.pgm", ff_config.CLOUD_MASK)
    logger.info("Building snow mask")
    ff_config.SNOW_MASK = path.join(ff_config.SCRATCH_PATH, "snow_mask.png")
    img.build_mask_files(ff_config, "snow_lut.pgm", ff_config.SNOW_MASK)
    ff_config.INPUT_FILE = ff_config.WATER_MASK

    if ff_config.ASSEMBLE_IMAGE:
        logger.info("Processing source data to remove negative pixels")
        clamp = img.clamp_image
        boost = img.boost_image
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
        img.assemble_image(ff_config)
    else:
        logger.info("Skipping scene generation")

    if ff_config.SLICE_IMAGE:
        logger.info(
            "Generating scene tiles of " +
            str(ff_config.GRID_SIZE) + "x" +
            str(ff_config.GRID_SIZE)+" pixels")
        img.prepare_tiles(ff_config)
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
        land = img.generate_rectangles(no_water, ff_config.width, ff_config.GRID_SIZE)
        clouds = img.generate_rectangles(too_cloudy, ff_config.width, ff_config.GRID_SIZE)
        water = img.generate_rectangles(retained_tiles, ff_config.width, ff_config.GRID_SIZE)
        img.draw_visualization(land, clouds, water, ff_config)

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

