from .image_operations.resize_image import ResizeImage
from .noop import NoOp

operations = {
    'resize_image': ResizeImage,
    'noop': NoOp
}
