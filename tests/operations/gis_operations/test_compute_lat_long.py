from unittest import TestCase
from unittest.mock import call, patch, MagicMock, Mock, PropertyMock, ANY

from theia.operations.gis_operations import ComputeLatLong
from theia.api.models import ImageryRequest, JobBundle, PipelineStage

class TestComputeLatLong(TestCase):
    def setUp(self):
        self.request = ImageryRequest(adapter_name='dummy')
        self.stage = PipelineStage(
            select_images=['composite'],
            sort_order=3,
            config={
                'output_filename': 'foo.csv',
            },
        )
        self.bundle = JobBundle(current_stage=self.stage, imagery_request=self.request)
        self.operation = ComputeLatLong(self.bundle)

    @patch('theia.operations.gis_operations.ComputeLatLong.convert_to_lat_long', side_effect=[(5.0, 6.0), (7.0, 8.0)])
    def test_commit_lat_long_values_for_row(self, mock_object):
        row_with_lat_long = self.operation.add_lat_long_values_to_row(
            {
             'x' : 1.0,
             'y' : 2.0,
             'utm_left' : 3.0,
             'utm_top' : 3.0,
             'utm_right' : 3.0,
             'utm_bottom' : 3.0,
             'utm_zone': 15,
             }
        )
        assert all(expected in row_with_lat_long.keys() for expected in ["x","y","utm_left","utm_top","utm_right","utm_bottom"])
        assert row_with_lat_long.get('top_left_latitude')==5.0
        assert row_with_lat_long.get('top_left_longitude')==6.0
        assert row_with_lat_long.get('bottom_right_latitude')==7.0
        assert row_with_lat_long.get('bottom_right_longitude')==8.0

    @patch('pyproj.proj.Proj.__call__', return_value=('latitude_number', 'longitude_number'))
    @patch('pyproj.proj.Proj.__init__', return_value=None)
    def test_convert_to_lat_long(self, mock_init, mock_call):
        latitude, longitude = self.operation.convert_to_lat_long(1.0, 2.0, 15)

        mock_init.assert_called_once_with(proj='utm', zone=15, ellps='WGS84')
        mock_call.assert_called_once_with(1.0, 2.0, inverse=True)

        assert latitude == 'latitude_number'
        assert longitude == 'longitude_number'