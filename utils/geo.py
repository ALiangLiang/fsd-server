import math

from geopy.distance import Distance, distance as distance_between

from messages.Position import Position
from utils.bearing import Bearing


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
