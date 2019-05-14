from theia.operations import image_operations
from theia.operations.noop import NoOp


operations = {
    'image_operations.resize_image': image_operations.ResizeImage,
    'noop': NoOp
}
