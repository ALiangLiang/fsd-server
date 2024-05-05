import math
import struct

from geopy.distance import Distance, distance as distance_between

from messages.Position import Position
from utils.bearing import Bearing
from helpers import get_mag_var_table


def calculate_initial_compass_bearing(start, end):
    lat1 = math.radians(start.latitude)
    lat2 = math.radians(end.latitude)

    diffLong = math.radians(end.longitude - start.longitude)

    x = math.sin(diffLong) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - (math.sin(lat1)
                                           * math.cos(lat2) * math.cos(diffLong))

    initial_bearing = math.atan2(x, y)

    # Now we have the initial bearing but math.atan2 return values
    # from -180° to + 180° which is not what we want for a compass bearing
    # The solution is to normalize the initial bearing as shown below
    initial_bearing = math.degrees(initial_bearing)
    compass_bearing = (initial_bearing + 360) % 360

    return Bearing(compass_bearing)


def fix_radial_distance(position: Position, bearing: Bearing, distance: Distance):
    dest_point = distance_between(
        meters=distance.meters).destination(position, bearing=bearing.degrees)
    return Position.from_point(dest_point)


def get_bearing_distance(position1: Position, position2: Position):
    distance = distance_between(position1, position2)
    bearing = calculate_initial_compass_bearing(position1, position2)
    return (bearing, distance)


def get_mag_var_by_position(position: Position):
    def offset(lon_x: float, lat_y: float):
        if lon_x == -180:
            lon_x = 180

        if 0 <= lon_x <= 180:
            # For positive (East) longitudes (from 0 to 180):
            # East: Offset = (Long*362)+(Lat*2)+180
            return ((lon_x * 362) + (lat_y * 2) + 180) // 2
        elif -180 <= lon_x <= -1:
            # For negative (West) longitudes (from -1 to -179):
            # West: Offset =((Long+360)*362)+(Lat*2)+180
            return (((lon_x + 360) * 362) + (lat_y * 2) + 180) // 2
        else:
            print("MagDecReader invalid coordinates in offset calculation", lon_x, lat_y)
            return 0

    mag_var_table = get_mag_var_table()
    lon_x = position.longitude
    lat_y = position.latitude

    min_lon_x1 = math.floor(lon_x)
    max_lon_x2 = math.ceil(lon_x)
    min_lat_y1 = math.floor(lat_y)
    max_lat_y2 = math.ceil(lat_y)

    # if position.nearGrid(1.0, Pos.POS_EPSILON_500M):
    #     # Exact or near degree - nothing to interpolate
    #     return struct.unpack('d', mag_var_table[offset(round(lon_x), round(lat_y))])
    # else:
    # Get four exact degree points around the coordinate
    top_right_offset_q12 = offset(min_lon_x1, max_lat_y2)
    top_left_offset_q22 = offset(max_lon_x2, max_lat_y2)
    bottom_right_offset_q11 = offset(max_lon_x2, min_lat_y1)
    bottom_left_offset_q21 = offset(min_lon_x1, min_lat_y1)

    # Calculate magvar values for the four points
    f_q12 = mag_var_table[top_right_offset_q12]
    f_q22 = mag_var_table[top_left_offset_q22]
    f_q11 = mag_var_table[bottom_right_offset_q11]
    f_q21 = mag_var_table[bottom_left_offset_q21]

    # Do a bilinear interpolation between the four points
    diff_x = max_lon_x2 - min_lon_x1
    if abs(diff_x) > 0.0:
        f_r1 = (max_lon_x2 - lon_x) / diff_x * f_q11 + \
            (lon_x - min_lon_x1) / diff_x * f_q21
        f_r2 = (max_lon_x2 - lon_x) / diff_x * f_q12 + \
            (lon_x - min_lon_x1) / diff_x * f_q22
    else:
        f_r1 = (f_q11 + f_q21) / 2.0
        f_r2 = (f_q12 + f_q22) / 2.0

    diff_y = max_lat_y2 - min_lat_y1
    if abs(diff_y) > 0.0:
        return (max_lat_y2 - lat_y) / diff_y * f_r1 + (lat_y - min_lat_y1) / diff_y * f_r2
    return (f_r1 + f_r2) / 2.0
