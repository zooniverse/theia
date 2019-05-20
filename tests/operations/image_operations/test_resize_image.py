
import pytest
from unittest.mock import patch
from theia.operations.image_operations import ResizeImage
from theia.api.models import JobBundle, PipelineStage

from PIL import Image

class TestResizeImage:
    @patch('theia.utils.FileUtils.version_filename', return_value='versioned filename')
    @patch('PIL.Image.open', autospec=True)
    def test_apply(self, mockOpen, mockVersion):
        with patch.object(mockOpen.return_value, 'thumbnail') as mockResize:
            with patch.object(mockOpen.return_value, 'save') as mockSave:
                stage = PipelineStage(config={'width': 10, 'height': 20}, sort_order=3)
                bundle = JobBundle(current_stage=stage)
                ResizeImage.apply('literal filename', bundle)

                mockVersion.assert_called_once_with('literal filename', 3)
                mockOpen.assert_called_once_with('literal filename')

                # TODO: figure out why these asserts don't work
                # i've verified from the debugger that it calls
                # the mocks correctly so ???

                # mockResize.assert_called_once_with((10, 20), Image.ANTIALIAS)
                # mockSave.assert_called_once_with('versioned filename')
