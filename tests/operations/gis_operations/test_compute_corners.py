import pytest
from unittest import TestCase
from unittest.mock import call, patch, MagicMock, Mock, PropertyMock, ANY
from PIL import Image

from theia.operations.gis_operations import ComputeCorners
from theia.api.models import ImageryRequest, JobBundle, PipelineStage


class TestComputeCorners(TestCase):
    def setUp(self):
        self.request = ImageryRequest(adapter_name='dummy')
        self.stage = PipelineStage(
            select_images=['composite'],
            sort_order=3,
            config={
                'tile_size': 100,
                'tile_overlap': 10,
                'output_filename': 'foo.csv',
            },
        )
        self.bundle = JobBundle(current_stage=self.stage, imagery_request=self.request)
        self.operation = ComputeCorners(self.bundle)

    @patch('theia.operations.gis_operations.ComputeCorners.top_edge', new_callable=PropertyMock, return_value=10)
    @patch('theia.operations.gis_operations.ComputeCorners.bottom_edge', new_callable=PropertyMock, return_value=110)
    @patch('theia.operations.gis_operations.ComputeCorners.scene_height', new_callable=PropertyMock, return_value=1000)
    def test_y_scale(self, *args):
        assert(self.operation.y_scale==0.1)

    @patch('theia.operations.gis_operations.ComputeCorners.left_edge', new_callable=PropertyMock, return_value=10)
    @patch('theia.operations.gis_operations.ComputeCorners.right_edge', new_callable=PropertyMock, return_value=110)
    @patch('theia.operations.gis_operations.ComputeCorners.scene_width', new_callable=PropertyMock, return_value=1000)
    def test_x_scale(self, *args):
        assert(self.operation.x_scale==0.1)

    @patch('theia.operations.gis_operations.ComputeCorners.get_new_version', return_value='new version')
    @patch('theia.operations.gis_operations.ComputeCorners.get_new_filename', return_value='new filename')
    def test_output_filename(self, mock_new, mock_version):
        assert(self.operation.output_filename=='new version')
        mock_new.assert_called_once_with('foo.csv')
        mock_version.assert_called_once_with('new filename')

    @patch('theia.operations.gis_operations.ComputeCorners.tile_overlap', new_callable=PropertyMock, return_value=10)
    @patch('theia.operations.gis_operations.ComputeCorners.tile_size', new_callable=PropertyMock, return_value=100)
    def test_stagger(self, *args):
        assert(self.operation.stagger==90)

    def test_tile_overlap(self):
        assert(self.operation.tile_overlap==10)

    def test_tile_size(self):
        assert(self.operation.tile_size==100)

    @patch('theia.operations.gis_operations.ComputeCorners.x_scale', new_callable=PropertyMock, return_value=0.1)
    @patch('theia.operations.gis_operations.ComputeCorners.left_edge', new_callable=PropertyMock, return_value=10)
    @patch('theia.operations.gis_operations.ComputeCorners.scene_width', new_callable=PropertyMock, return_value=1000)
    def test_transform_x(self, mock_width, mock_left, mock_scale):
        assert(self.operation.transform_x(500)==60)
        assert(self.operation.transform_x(1000)==110)
        assert(self.operation.transform_x(1500)==110)

    @patch('theia.operations.gis_operations.ComputeCorners.y_scale', new_callable=PropertyMock, return_value=0.1)
    @patch('theia.operations.gis_operations.ComputeCorners.top_edge', new_callable=PropertyMock, return_value=10)
    @patch('theia.operations.gis_operations.ComputeCorners.scene_height', new_callable=PropertyMock, return_value=1000)
    def test_transform_y(self, *args):
        assert(self.operation.transform_y(500)==60)
        assert(self.operation.transform_y(1000)==110)
        assert(self.operation.transform_y(1500)==110)

    def test_edges(self):
        self.operation._topleft = (1, 2,)
        self.operation._bottomright = (3, 4,)

        assert(self.operation.left_edge == 1)
        assert(self.operation.top_edge == 2)
        assert(self.operation.right_edge == 3)
        assert(self.operation.bottom_edge == 4)

    @patch('theia.adapters.dummy.Adapter.get_metadata', side_effect=['l', 't', 'r', 'b'])
    def test_get_scene_coords(self, *args):
        assert(self.operation.get_scene_coords()==(['l', 't'], ['r', 'b']))

    @patch('PIL.Image.open', return_value=MagicMock())
    def test_get_image_dimensions(self, mock_open):
        mock_enter = mock_open.return_value.__enter__

        p = PropertyMock()
        type(mock_enter.return_value).size = p

        self.operation.get_image_dimensions('somefile')

        mock_open.assert_called_once_with('somefile')
        p.assert_called_once()

    @patch('theia.operations.gis_operations.ComputeCorners.transform_y')
    @patch('theia.operations.gis_operations.ComputeCorners.transform_x')
    def test_write_one(self, mock_tx, mock_ty):
        mock_tx.side_effect = [10, 12]
        mock_ty.side_effect = [11, 13]
        mock = Mock()

        self.operation.write_one(mock, 0, 1, 2, 3)

        mock.writerow.assert_called_once_with({
            'x': 0,
            'y': 1,
            'utm_left': 10,
            'utm_right': 12,
            'utm_top': 11,
            'utm_bottom': 13
        })

    @patch('theia.operations.gis_operations.ComputeCorners.stagger', new_callable=PropertyMock, return_value=9)
    @patch('theia.operations.gis_operations.ComputeCorners.scene_width', new_callable=PropertyMock, return_value=25)
    @patch('theia.operations.gis_operations.ComputeCorners.scene_height', new_callable=PropertyMock, return_value=24)
    @patch('theia.operations.gis_operations.ComputeCorners.write_one')
    def test_write_all(self, mock_write, *args):
        writer = Mock()

        self.operation.write_all(writer)

        assert(mock_write.call_count==9)
        mock_write.assert_has_calls([
            call(writer, 0, 0, ANY, ANY),
            call(writer, 0, 2, ANY, ANY),
            call(writer, 2, 0, ANY, ANY),
            call(writer, 2, 2, ANY, ANY),
        ], any_order=True)

    @patch('theia.operations.gis_operations.ComputeCorners.write_all')
    @patch('theia.operations.gis_operations.ComputeCorners.output_filename', new_callable=PropertyMock, return_value='new filename')
    @patch('theia.operations.gis_operations.compute_corners.open', create=True, return_value=MagicMock())
    @patch('theia.operations.gis_operations.ComputeCorners.get_scene_coords', return_value=([0,0], [10,10]))
    @patch('theia.operations.gis_operations.ComputeCorners.get_image_dimensions', return_value=(0,0))
    def test_apply(self, mock_dims, mock_coords, mock_open, mock_output, mock_write):
        self.operation.apply(['some image'])

        mock_dims.assert_called_once_with('some image')
        mock_write.assert_called_once()
        mock_open.assert_called_once()
