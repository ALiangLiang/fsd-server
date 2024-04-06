from typing import TypedDict
import re

class Fix(TypedDict):
    position: Position
    ident: str
    type: str
    region: str


async def read_earth_fix() -> dict[str, Fix]:
    fixesMap: dict[str, Fix] = {}
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
