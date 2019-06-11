from theia.operations import image_operations, panoptes_operations
from theia.operations.noop import NoOp


operations = {
    'image_operations.resize_image': image_operations.ResizeImage,
    'image_operations.shallow_image': image_operations.ShallowImage,
    'panoptes_operations.upload_subject': panoptes_operations.UploadSubject,
    'noop': NoOp
}
