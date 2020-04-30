import csv
from PIL import Image

from ..abstract_operation import AbstractOperation
from os import path
import logging

from os import path, mkdir, listdir
from shutil import rmtree, copy
import tempfile


# https://docs.python.org/3/library/csv.html

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


def parse_options(filenames):
    ff_config.SCENE_NAME = path.dirname(filenames[0])
    ff_config.NEW_MASK = path.join(ff_config.SCENE_DIR, ff_config.SCENE_NAME + "_pixel_qa.tif")
    ff_config.METADATA_SRC = path.join(ff_config.SCENE_DIR, ff_config.SCENE_NAME + ".xml")
    ff_config.INPUT_FILE = ff_config.NEW_MASK

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




