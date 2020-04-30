from __future__ import division
from pyproj import Proj

def compute_lat_lon(x, y, utm_zone):
    p = Proj(proj='utm', zone=utm_zone, ellps='WGS84')
    lat, lon = p(x, y, inverse=True)
    return [lat, lon]

def compute_tile_coords(row, col, width, height, config):
    scene_top = float(config.METADATA["#scene_corner_UL_y"])
    scene_bottom = float(config.METADATA["#scene_corner_LR_y"])
    scene_left = float(config.METADATA["#scene_corner_UL_x"])
    scene_right = float(config.METADATA["#scene_corner_LR_x"])

    scene_span_x = scene_right - scene_left
    scene_span_y = scene_bottom - scene_top

    left = scene_left + ((col * config.GRID_SIZE) / config.width) * scene_span_x
    top = scene_top + ((row * config.GRID_SIZE) / config.height) * scene_span_y
    right = left + (width / config.width) * scene_span_x
    bottom = top + (height / config.height) * scene_span_y

    return [left, top, right, bottom]

def compute_coordinate_metadata(row, col, width, height, config):
    [left, top, right, bottom] = compute_tile_coords(row, col, width, height, config)
    tile_center_x = (left+right)/2
    tile_center_y = (top+bottom)/2

    [lon, lat] = compute_lat_lon(tile_center_x, tile_center_y, config.METADATA['#utm_zone'])

    return {
        '#tile_UL_x': left,
        '#tile_UL_y': top,
        '#tile_UR_x': right,
        '#tile_UR_y': top,
        '#tile_LL_x': left,
        '#tile_LL_y': bottom,
        '#tile_LR_x': right,
        '#tile_LR_y': bottom,

        '#tile_center_x': tile_center_x,
        '#tile_center_y': tile_center_y,

        'center_lat': lat,
        'center_lon': lon,
        'map_link': generate_map_link(lat, lon)
    }


def generate_map_link(lat, lon):
    return "http://maps.google.com/maps?q={0}+{1}&ll={0},{1}&t=k&z=12".format(lat, lon)
