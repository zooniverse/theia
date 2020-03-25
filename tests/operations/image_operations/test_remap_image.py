import pytest
from unittest.mock import patch, Mock

import numpy as np

from theia.operations.image_operations import RemapImage
from theia.api.models import ImageryRequest, JobBundle, PipelineStage


class TestRemapImage:
    dummy_array = np.array([[1, 1, 1], [1, 1, 1]], dtype=np.int64)

    @patch('theia.adapters.dummy.Adapter.remap_pixel')
    @patch('theia.operations.AbstractOperation.get_new_version', return_value='versioned filename')
    @patch('libtiff.TIFF.open', return_value=Mock())
    @patch('PIL.Image.fromarray', return_value=Mock())
    def test_do_apply(self, mockFromArray, mockOpen, mockRename, mockRemap):
        mockRemap.return_value = self.dummy_array
        mockOpen.return_value.read_image.return_value = self.dummy_array

        request = ImageryRequest(adapter_name='dummy')
        stage = PipelineStage(config={}, sort_order=3)
        bundle = JobBundle(current_stage=stage, imagery_request=request)

        operation = RemapImage(bundle)
        operation.apply(['literal filename'])

        mockRename.assert_called_once_with('literal filename')
        mockOpen.assert_called_once_with('literal filename')
        mockOpen.return_value.read_image.assert_called_once_with()
        mockRemap.assert_called_once_with(self.dummy_array)
        mockFromArray.assert_called_once_with(self.dummy_array)

        mockFromArray.return_value.save.assert_called_once()
        first_method_call = mockFromArray.return_value.save.call_args_list[0]
        args = first_method_call[0]
        assert str.endswith(args[0], '/theia/3_/versioned filename')

