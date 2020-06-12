import logging
from os import path, mkdir, listdir
from shutil import rmtree, copy
import tempfile

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

def get_files_by_extension(filepath, extension):
    accum = []

    files = listdir(filepath)

    for filename in files:
        if filename.endswith(extension):
            accum.append(filename)

    return accum

def maybe_clean_scratch(config):
    logger = logging.getLogger(config.SCENE_NAME)
    if config.WITHTEMPDIR:
        logger.info("attempting to clean up scratch directory")
        rmtree(config.SCRATCH_PATH)
