from typing import TypedDict
from geopy.distance import Distance, distance as distance_between
import math
import re

from messages.Position import Position


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

    return compass_bearing


def fix_radial_distance(position: Position, bearing, distance: Distance):
    dest_point = distance_between(
        meters=distance.meters).destination(position, bearing=bearing)
    return Position.from_point(dest_point)


def get_bearing_distance(position1: Position, position2: Position):
    distance = distance_between(position1, position2)
    bearing = calculate_initial_compass_bearing(position1, position2)
    return (bearing, distance)


class Fix(TypedDict):
    position: Position
    ident: str
    type: str
    region: str


async def read_earth_fix() -> dict[str, Fix]:
    fixesMap = {}
    with open("earth_fix.dat", "r") as file:
        for line in file:
            if line[0] != " ":
                continue
            latitude, longitude, ident, type_, region, _ = re.sub(
                "  +", " ", line.strip()).split(" ")
            if region != "RC":
                continue
            fixesMap[ident] = {
                "position": Position(float(latitude), float(longitude)),
                "ident": ident,
                "type": type_,
                "region": region,
            }
    return fixesMap


class Navaid(Fix):
    name: str


async def read_earth_nav() -> dict[str, Navaid]:
    navsMap: dict[str, Navaid] = {}
    with open("earth_nav.dat", "r", encoding="utf-8") as file:
        for line in file:
            if line[0] != " ":
                continue

            _, latitude, longitude, _, _, _, _, ident, type_, region, name, *_ = line.strip(
            ).replace("  +", " ").split(" ")
            if region != "RC":
                continue
            navsMap[ident] = {
                "position": Position(float(latitude), float(longitude)),
                "ident": ident,
                "type": type_,
                "region": region,
                "name": name,
            }
    return navsMap


class Procedure(TypedDict):
    ident: str
    type: str
    runway: str
    navaids: list[dict]


async def read_procedures(airport, fixes) -> dict[str, Procedure]:
    procedures: dict[str, Procedure] = {}
    with open(f"CIFP/{airport}.dat", "r") as file:
        for line in file:
            if line == "":
                continue

            type_n_seq, _, ident, runway, navaid, * \
                _ = line.strip().replace(" ", "").split(",")
            type_, seq = type_n_seq.split(":")
            if type_ == "RWY":
                continue
            if ident not in procedures:
                procedures[ident] = {"navaids": []}
            fix = fixes.get(navaid, None)
            if fix is not None:
                procedures[ident]["ident"] = ident
                procedures[ident]["type"] = type_
                procedures[ident]["runway"] = runway
                procedures[ident]["navaids"].append(fix)
    return procedures
