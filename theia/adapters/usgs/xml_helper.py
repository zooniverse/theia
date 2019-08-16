import re
from lxml import etree


class XmlHelper:
    METADATA_PATHS = {
        'acquired_date': 'espa:global_metadata/espa:acquisition_date/text()',
        'acquired_time': 'espa:global_metadata/espa:scene_center_time/text()',
        'earth_sun_distance': 'espa:global_metadata/espa:earth_sun_distance/text()',
        'scene_corner_BR_x': 'espa:global_metadata/espa:projection_information/espa:corner_point[@location="BR"]/@x',
        'scene_corner_BR_y': 'espa:global_metadata/espa:projection_information/espa:corner_point[@location="BR"]/@y',
        'scene_corner_UL_x': 'espa:global_metadata/espa:projection_information/espa:corner_point[@location="UL"]/@x',
        'scene_corner_UL_y': 'espa:global_metadata/espa:projection_information/espa:corner_point[@location="UL"]/@y',
        'sensor_id': 'espa:global_metadata/espa:instrument/text()',
        'spacecraft': 'espa:global_metadata/espa:satellite/text()',
        'sun_azimuth': 'espa:global_metadata/espa:solar_angles/@azimuth',
        'sun_zenith': 'espa:global_metadata/espa:solar_angles/@zenith',
        'utm_zone': 'espa:global_metadata/espa:projection_information/espa:utm_proj_params/espa:zone_code/text()'
    }

    def __init__(self, file_name):
        self.file_name = file_name
        self.tree = None
        self.nsmap = None

    def resolve(self, field_name):
        field_name = re.sub('\W+', '', field_name)
        return XmlHelper.METADATA_PATHS.get(field_name, None)

    def retrieve(self, field_name):
        path = self.resolve(field_name)
        tree = self.get_tree()
        return tree.xpath(path, namespaces=self.nsmap)

    def get_tree(self):
        if not self.tree:
            self.tree = etree.parse(self.file_name)
            self.nsmap = {"espa": self.tree.getroot().nsmap[None]}

        return self.tree
