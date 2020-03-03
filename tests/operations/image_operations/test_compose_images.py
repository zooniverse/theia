import pytest
from unittest.mock import call, patch, Mock, ANY
from PIL import Image

from theia.operations.image_operations import ComposeImages
from theia.api.models import ImageryRequest, JobBundle, PipelineStage


class TestComposeImages:
    @patch('theia.operations.AbstractOperation.get_new_version', return_value='totally new name')
    @patch('theia.operations.AbstractOperation.get_new_filename', return_value='new name')
    @patch('PIL.Image.open', side_effect=[Mock(), Mock(), Mock()])
    @patch('PIL.Image.merge', return_value=Mock())
    def test_apply(self, mock_merge, mock_open, mock_get_new, mock_get_version):
        request = ImageryRequest(adapter_name='dummy')
        stage = PipelineStage(
            select_images=['green_channel', 'red_channel', 'blue_channel'],
            config={"red": "red_channel", "green": "green_channel", "blue": "blue_channel", "filename": "newish name"},
            sort_order=3
        )
        bundle = JobBundle(current_stage=stage, imagery_request=request)

        operation = ComposeImages(bundle)
        operation.apply(['green_tif', 'red_tif', 'blue_tif'])

        mock_open.assert_has_calls([call('green_tif'), call('red_tif'), call('blue_tif')])
        mock_merge.assert_called_once_with('RGB', (ANY, ANY, ANY))
        mock_merge.return_value.save.assert_called_once_with('/Users/chelseatroy/workspace/theia/3_/totally new name')
