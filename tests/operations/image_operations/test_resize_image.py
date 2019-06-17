import pytest
from unittest.mock import patch, Mock
from PIL import Image

from theia.operations.image_operations import ResizeImage
from theia.api.models import JobBundle, PipelineStage

class TestResizeImage:
    @patch('theia.operations.AbstractOperation.get_new_version', return_value='new filename')
    @patch('PIL.Image.open', return_value=Mock())
    def test_apply(self, mock_open, mock_get_name):
        stage = PipelineStage(config={'width': 10, 'height': 20}, sort_order=3)
        bundle = JobBundle(current_stage=stage)

        operation = ResizeImage(bundle)
        operation.apply(['literal filename'])

        mock_get_name.assert_called_once_with('literal filename')

        mock_open.assert_called_once_with('literal filename')
        mock_open.return_value.thumbnail.assert_called_once_with((10, 20), Image.ANTIALIAS)
        mock_open.return_value.save.assert_called_once_with('new filename')
