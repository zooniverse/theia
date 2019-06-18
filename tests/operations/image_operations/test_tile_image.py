import pytest
import numpy as np
from unittest.mock import call, patch, Mock, MagicMock, PropertyMock

from theia.api import models
from theia.operations.image_operations import TileImage

class TestTileImage:
    @patch('theia.operations.image_operations.TileImage.tile_one')
    def test_apply(self, mock_one):
        bundle = models.JobBundle()
        operation = TileImage(bundle)
        operation.apply(['a', 'b'])

        assert(mock_one.call_count==2)

    @patch('os.path.split', return_value=('split', None))
    @patch('os.path.splitext', return_value=('stripped', None))
    @patch('PIL.Image.open', return_value=MagicMock())
    @patch('numpy.asarray', return_value=np.zeros((300,300,3)))
    @patch('theia.operations.image_operations.TileImage.build_row')
    def test_tile_one(self, mock_row, mock_array, mock_open, *args):
        mock_open.return_value.__enter__ = Mock()
        mock_enter = mock_open.return_value.__enter__
        mock_enter.return_value.height=300

        stage = models.PipelineStage(
            output_format='jpg',
            config={'tile_size': 100, 'tile_overlap': 10}
        )

        bundle = models.JobBundle(current_stage=stage)
        operation = TileImage(bundle)
        operation.tile_one('a')

        mock_open.assert_called_once_with('a')
        mock_array.assert_called_once_with(mock_open.return_value.__enter__.return_value)

        calls = [
            call('stripped', 0, 0, mock_array.return_value, mock_enter.return_value.width),
            call('stripped', 90, 1, mock_array.return_value, mock_enter.return_value.width),
            call('stripped', 180, 2, mock_array.return_value, mock_enter.return_value.width),
            call('stripped', 270, 3, mock_array.return_value, mock_enter.return_value.width),
        ]

        mock_row.assert_has_calls(calls)
        assert(mock_row.call_count==4)

    def test_construct_tile_name(self):
        stage = models.PipelineStage(
            output_format='jpg',
            config={'output_directory': 'foo'}
        )

        bundle = models.JobBundle(current_stage=stage)
        operation = TileImage(bundle)
        assert(operation.construct_tile_name('f', 3, 4)=='foo/f_tile_004_003.jpg')

    @patch('theia.operations.image_operations.TileImage.construct_tile_name', return_value='a tile name')
    @patch('theia.operations.image_operations.TileImage.build_tile')
    def test_build_row(self, mock_build, mock_name):
        pixels = np.zeros((300, 300, 4))

        stage = models.PipelineStage(
            output_format='jpg',
            config={'tile_size': 100, 'tile_overlap': 10}
        )

        bundle = models.JobBundle(current_stage=stage)
        operation = TileImage(bundle)
        operation.build_row('f', 90, 1, pixels, 300)

        mock_name.assert_has_calls([
            call('f', 0, 1),
            call('f', 1, 1),
            call('f', 2, 1),
        ])
        assert(mock_name.call_count==4)

        mock_build.assert_has_calls([
            call(pixels, 90, 0, 'a tile name'),
            call(pixels, 90, 90, 'a tile name'),
            call(pixels, 90, 180, 'a tile name'),
        ])
        assert(mock_build.call_count==4)

    @patch('PIL.Image.fromarray', return_value=MagicMock())
    def test_build_tile(self, mock_array):
        mock_array.return_value.__enter__ = Mock()
        mock_enter = mock_array.return_value.__enter__
        pixels = np.zeros((300, 300, 4))

        stage = models.PipelineStage(
            output_format='jpg',
            config={'tile_size': 100, 'tile_overlap': 10}
        )

        bundle = models.JobBundle(current_stage=stage)
        operation = TileImage(bundle)

        operation.build_tile(pixels, 180, 90, 'f')

        np.testing.assert_array_equal(np.zeros((100, 100, 4)), mock_array.call_args[0][0])
        mock_enter.return_value.save.assert_called_once_with('f')

