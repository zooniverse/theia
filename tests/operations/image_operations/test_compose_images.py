import pytest
from unittest.mock import call, patch, Mock, ANY
from PIL import Image

from theia.operations.image_operations import ComposeImages
from theia.api.models import ImageryRequest, JobBundle, PipelineStage


class TestComposeImages:
    @pytest.mark.focus
    @patch('theia.operations.AbstractOperation.get_new_filename', return_value='totally new name')
    @patch('PIL.Image.open', side_effect=[Mock(), Mock(), Mock()])
    @patch('PIL.Image.merge', return_value=Mock())
    def test_apply(self, mock_merge, mock_open, mock_get_new):
        request = ImageryRequest(adapter_name='dummy')
        stage = PipelineStage(
            select_images=['ggggg', 'rrr', 'bbbb'],
            config={'red': 'rrr', 'green': 'ggggg', 'blue': 'bbbb', 'filename': 'newish name'},
            sort_order=3
        )
        bundle = JobBundle(current_stage=stage, imagery_request=request)

        operation = ComposeImages(bundle)
        operation.apply(['neerg', 'erd', 'eulb'])

        mock_get_new.assert_called_once_with('newish name')
        mock_open.assert_has_calls([call('erd'), call('neerg'), call('eulb')])
        mock_merge.assert_called_once_with('RGB', (ANY, ANY, ANY))
        mock_merge.return_value.save.assert_called_once_with('totally new name')
