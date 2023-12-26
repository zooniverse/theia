import pytest
from unittest.mock import patch, Mock
from PIL import Image

from theia.operations.image_operations import ResizeImage
from theia.api.models import JobBundle, PipelineStage

class TestResizeImage:
    @patch('PIL.Image.open', return_value=Mock())
    def test_apply(self, mock_open):
        stage = PipelineStage(config={"width": 10, "height": 20}, sort_order=3)
        bundle = JobBundle(current_stage=stage)

        operation = ResizeImage(bundle)
        operation.apply(["literal filename"])

        mock_open.assert_called_once_with('literal filename')
        mock_open.return_value.thumbnail.assert_called_once_with((10, 20), Image.LANCZOS)
        mock_open.return_value.save.assert_called_once()
        first_method_call = mock_open.return_value.save.call_args_list[0]
        args = first_method_call[0]
        assert str.endswith(args[0], '/3_/literal filename_resized_to_10_20.tif')
