import pytest
from unittest.mock import patch, Mock
from PIL import Image

from theia.operations.image_operations import ResizeImage
from theia.api.models import JobBundle, PipelineStage

class TestResizeImage:
    @pytest.mark.focus
    @patch('theia.utils.FileUtils.version_filename', return_value='versioned filename')
    @patch('PIL.Image.open', return_value=Mock())
    def test_apply(self, mockOpen, mockVersion):
        stage = PipelineStage(config={'width': 10, 'height': 20}, sort_order=3)
        bundle = JobBundle(current_stage=stage)
        ResizeImage.apply('literal filename', bundle)

        mockVersion.assert_called_once_with('literal filename', 3)
        mockOpen.assert_called_once_with('literal filename')

        mockOpen.return_value.thumbnail.assert_called_once_with((10, 20), Image.ANTIALIAS)
        mockOpen.return_value.save.assert_called_once_with('versioned filename')
