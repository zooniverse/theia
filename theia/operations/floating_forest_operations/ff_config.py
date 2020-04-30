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
