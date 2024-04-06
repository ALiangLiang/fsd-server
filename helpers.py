from datetime import timedelta

from geopy.distance import Distance
from sqlalchemy.orm import joinedload

from db.init import session
from db.models import Airport, Airway, Approach, ProcedureLeg, Waypoint, Vor, Runway, TransitionLeg
from utils.leg import Leg
from utils.physics import Acceleration


def get_waypoints_by_ident_n_region(ident: str, region: str):
    return session.query(Waypoint).filter(Waypoint.ident == ident, Waypoint.region == region).all()


def get_vors_by_ident_n_region(ident: str, region: str):
    return session.query(Vor).filter(Vor.ident == ident, Vor.region == region).all()


def get_runway_end_by_airport_n_runway(dep_airport: str, dep_runway: str):
    airport = session.query(Airport).options(
        joinedload(Airport.runways)
        .options(joinedload(Runway.primary_end))
        .options(joinedload(Runway.secondary_end))
    ).filter(Airport.ident == dep_airport).first()
    if (airport is None):
        return None
    for runway in airport.runways:
        if runway.primary_end.name == dep_runway:
            return runway.primary_end
        if runway.secondary_end.name == dep_runway:
            return runway.secondary_end


def get_fix_by_ident(ident: str, region: str | None = None):
    _query = session.query(Waypoint).filter(Waypoint.ident == ident)
    if (region is not None):
        _query = _query.filter(Waypoint.region == region)
    return _query.first()


def fill_position_on_legs(procedure_leg: list[ProcedureLeg]):
    legs: list[Leg] = []
    for al in procedure_leg:
        if al.fix_lonx is not None and al.fix_laty is not None:
            continue

        if al.fix_type == 'R':  # runway
            runway_end_name = al.fix_ident[2:] if al.fix_ident.startswith(
                'RW') else al.fix_ident
            runway_end = get_runway_end_by_airport_n_runway(
                al.fix_airport_ident, runway_end_name)
            al.fix_lonx = runway_end.lonx
            al.fix_laty = runway_end.laty
            legs.append(Leg.from_procedure_leg(al))
        else:
            fix = get_fix_by_ident(al.fix_ident, al.fix_region)
            if fix is None:
                continue
            al.fix_lonx = fix.lonx
            al.fix_laty = fix.laty
            leg = Leg.from_procedure_leg(al)
            leg.waypoint = fix
            legs.append(leg)

    return legs


def get_start_leg(dep_airport: str, dep_runway: str):
    runway_end = get_runway_end_by_airport_n_runway(dep_airport, dep_runway)
    if runway_end is None:
        return None

    return Leg.from_runway_end(runway_end)


def get_sid_legs(dep_airport: str, dep_runway: str, sid: str):
    approach = session.query(Approach).options(
        joinedload(Approach.approach_legs)
    ).filter(Approach.airport_ident == dep_airport,
             Approach.runway_name == dep_runway,
             Approach.fix_ident == sid,
             Approach.suffix == 'D').first()
    if approach is None:
        return []
    return fill_position_on_legs(approach.approach_legs)


def get_star_legs(arr_airport: str, star: str):
    approach = session.query(Approach).options(
        joinedload(Approach.approach_legs)
    ).filter(Approach.airport_ident == arr_airport,
             Approach.fix_ident == star,
             Approach.suffix == "A").first()
    if approach is None:
        return []
    return fill_position_on_legs(approach.approach_legs)


def get_app_legs(arr_airport: str, app_name: str, transition_name: str | None = None):
    approach = session.query(Approach).options(
        joinedload(Approach.approach_legs)
    ).filter(Approach.airport_ident == arr_airport,
             Approach.arinc_name == app_name,
             Approach.suffix == None).first()
    if approach is None:
        return []

    transition_legs: list[TransitionLeg] = []
    if transition_name is not None:
        transition_legs = next(
            (t.transition_legs for t in approach.transitions if t.fix_ident == transition_name), [])

    legs = fill_position_on_legs(transition_legs + approach.approach_legs)
    not_missed_legs = []
    missed_legs = []
    for l in legs:
        if l.is_missed:
            missed_legs.append(l)
        else:
            not_missed_legs.append(l)
    return not_missed_legs, missed_legs


def get_all_airways(airway_name: str, fix: Waypoint):
    airway = session.query(Airway).filter(
        Airway.airway_name == airway_name,
        Airway.from_waypoint_id == fix.waypoint_id
    ).first()
    if airway is None:
        return []
    airways = session.query(Airway).filter(
        Airway.airway_name == airway_name,
        Airway.airway_fragment_no == airway.airway_fragment_no,
    ).order_by(Airway.sequence_no).all()
    return airways


def get_airways_between_fixs(airway: str, from_fix: Waypoint, to_fix_name: str):
    airways = get_all_airways(airway, from_fix)
    airway_range: list[Airway] = []
    for a in airways:
        if len(airway_range) == 0:
            if a.from_waypoint.ident == from_fix.ident or a.from_waypoint.ident == to_fix_name:
                airway_range.append(a)
        else:
            airway_range.append(a)
            if a.to_waypoint.ident == to_fix_name or a.from_waypoint.ident == from_fix.ident:
                return airway_range
    return []


def airways_to_legs(airways: list[Airway]):
    return [Leg.from_airway(a) for a in airways] + [Leg.from_airway_end(airways[-1])]


# ex. 121.800 -> @21800
def frequency_to_abbr(frequency: str):
    return '@' + frequency.replace('.', '')[1:]


def get_displacement_by_seconds(acceleration: Acceleration, time: timedelta, initial_speed: float = 0.0) -> Distance:
    """
    params:
        acceleration: m / s^2
        seconds: s
        initial_speed: m / s
    return:
        m
    """
    return acceleration * 0.5 * time * time + initial_speed * time


def get_legs_by_route_str(route_str: str):
    routes = route_str.split(' ')
    dep_airport, dep_runway = routes.pop(0).split('/')
    speed_n_flight_level = routes.pop(0)
    arr_airport, app_name = routes.pop(-1).split('/')

    items = [*routes]
    sid_name = items.pop(0)
    sid_to_fix = items.pop(0)
    star_name = items.pop(-1)

    # start
    legs = [get_start_leg(dep_airport, dep_runway)]
    print(legs)

    # SID
    legs.extend(
        get_sid_legs(dep_airport, dep_runway, sid_name)
    )

    # en-route
    while len(items) != 0:
        airway_name = items.pop(0)
        to_fix_name = items.pop(0)
        new_airways = get_airways_between_fixs(
            airway_name, legs[-1].waypoint, to_fix_name)
        new_legs = airways_to_legs(new_airways)
        extended_legs = new_legs[1:]
        legs.extend(extended_legs)

    # STAR
    star_legs = get_star_legs(arr_airport, star_name)
    extended_legs = star_legs[1:]
    legs.extend(extended_legs)

    # Approach
    app_legs, missed_app_legs = get_app_legs(arr_airport, app_name)
    extended_legs = app_legs[1:]
    legs.extend(extended_legs)

    return legs
