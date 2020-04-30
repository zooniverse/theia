import logging
from lxml import etree

def get_field_text(tree, path):
    nsmap = {"espa": tree.getroot().nsmap[None]}
    node = tree.xpath(path, namespaces=nsmap)
    if len(node) > 0:
        return node[0].text
    return ''

def parse_metadata(scene, xml_filename):
    logger = logging.getLogger(scene)
    logger.info("Parsing XML metadata from {0}".format(xml_filename))

    result = {'!scene': scene}

    tree = etree.parse(xml_filename)
    nsmap = {"espa": tree.getroot().nsmap[None]}

    result['acquired_date'] = get_field_text(tree, "espa:global_metadata/espa:acquisition_date")
    result['acquired_time'] = get_field_text(tree, "espa:global_metadata/espa:scene_center_time")
    result['sensor_id'] = get_field_text(tree, "espa:global_metadata/espa:instrument")
    result['spacecraft'] = get_field_text(tree, 'espa:global_metadata/espa:satellite')

    result['!earth_sun_distance'] = get_field_text(
        tree,
        "espa:global_metadata/espa:earth_sun_distance")

    angles = tree.xpath("espa:global_metadata/espa:solar_angles", namespaces=nsmap)
    if len(angles) > 0:
        result['!sun_azimuth'] = angles[0].get("azimuth")
        result['!sun_zenith'] = angles[0].get("zenith")

    covers = tree.xpath(
        "espa:bands/espa:band[@name='cfmask']/espa:percent_coverage/espa:cover",
        namespaces=nsmap)
    for cover in covers:
        if cover.get("type") == "cloud":
            result['!cloud_cover'] = cover.text
        if cover.get("type") == "water":
            result['!water_cover'] = cover.text

    result['#utm_zone'] = get_field_text(
        tree,
        "espa:global_metadata/espa:projection_information/espa:utm_proj_params/espa:zone_code")

    corners = tree.xpath(
        "espa:global_metadata/espa:projection_information/espa:corner_point",
        namespaces=nsmap)
    for corner in corners:
        result["#scene_corner_{0}_x".format(corner.get("location"))] = corner.get("x")
        result["#scene_corner_{0}_y".format(corner.get("location"))] = corner.get("y")

    return result
