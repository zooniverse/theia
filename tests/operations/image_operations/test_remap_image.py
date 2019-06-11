import pytest
from unittest.mock import patch

import numpy as np

from theia.operations.image_operations import RemapImage
from theia.api.models import ImageryRequest, JobBundle, PipelineStage


class MockTIFF:
    def read_image(self):
        pass


class MockImage:
    def convert(self, toType):
        pass

    def save(self, filename):
        pass


class TestRemapImage:
    dummy_array = np.array([[1, 1, 1], [1, 1, 1]], dtype=np.int64)

    @patch('theia.operations.image_operations.RemapImage.do_apply')
    def test_apply(self, mockApply):
        request = ImageryRequest(adapter_name='usgs')
        stage = PipelineStage(config={}, sort_order=3)
        bundle = JobBundle(current_stage=stage, imagery_request=request)
        RemapImage.apply('literal filename', bundle)
        mockApply.assert_called_once_with('usgs', 'literal filename', 3)

    @patch('theia.adapters.dummy.Adapter.remap_pixel')
    @patch('theia.utils.FileUtils.version_filename', return_value='versioned filename')
    @patch('libtiff.TIFF.open', return_value=MockTIFF())
    @patch('PIL.Image.fromarray', return_value=MockImage())
    def test_do_apply(self, mockFromArray, mockOpen, mockRename, mockRemap):
        mockRemap.return_value = self.dummy_array
        with patch.object(mockOpen.return_value, 'read_image') as mockRead:
            with patch.object(mockFromArray.return_value, 'convert') as mockConvert:
                with patch.object(mockFromArray.return_value, 'save') as mockSave:
                    mockRead.return_value=self.dummy_array

                    RemapImage.do_apply('dummy', 'input_filename', 2)

                    mockRename.assert_called_once_with('input_filename', 2)
                    mockOpen.assert_called_once_with('input_filename')
                    mockRead.assert_called_once_with()
                    mockRemap.assert_called_once_with(self.dummy_array)
                    mockFromArray.assert_called_once_with(self.dummy_array)
                    mockConvert.assert_called_once_with('L')
                    mockSave.assert_called_once_with('versioned filename')
