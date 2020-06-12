from theia.operations import gis_operations, image_operations, panoptes_operations, floating_forest_operations
from theia.operations.noop import AbstractOperation, NoOp


operations = {
    'floating_forest_operations.floating_forest': floating_forest_operations.FloatingForest,

    'gis_operations.compute_corners': gis_operations.ComputeCorners,

    'image_operations.resize_image': image_operations.ResizeImage,
    'image_operations.remap_image': image_operations.RemapImage,
    'image_operations.tile_image': image_operations.TileImage,
    'image_operations.compose_images': image_operations.ComposeImages,

    'panoptes_operations.upload_subject': panoptes_operations.UploadSubject,

    'noop': NoOp,
}
