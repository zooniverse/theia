import csv
from pyproj import Proj

from ..abstract_operation import AbstractOperation

class ComputeLatLong(AbstractOperation):
    def apply(self, filenames):
        pass

    # TODO: parse csv from string to integer

    def convert_to_lat_long(self, utm_x: float, utm_y: float, utm_zone: int):
        conversion_method = Proj(proj='utm', zone=utm_zone, ellps='WGS84')
        return conversion_method(utm_x, utm_y, inverse=True)

    def add_lat_long_values_to_row(self, utm_row_as_dictionary):
        top_left_lat, top_left_long = self.convert_to_lat_long(
            utm_row_as_dictionary['utm_left'],
            utm_row_as_dictionary['utm_top'],
            utm_row_as_dictionary['utm_zone'],
        )
        utm_row_as_dictionary.update({
            'top_left_latitude': top_left_lat,
            'top_left_longitude': top_left_long,
        })
        bottom_right_lat, bottom_right_long = self.convert_to_lat_long(
            utm_row_as_dictionary['utm_right'],
            utm_row_as_dictionary['utm_bottom'],
            utm_row_as_dictionary['utm_zone'],
        )
        utm_row_as_dictionary.update({
            'bottom_right_latitude': bottom_right_lat,
            'bottom_right_longitude': bottom_right_long,
        })
        return utm_row_as_dictionary
