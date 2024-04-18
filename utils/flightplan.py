from typing import Literal

from geopy.distance import Distance

from messages.FlightplanMessage import FlightplanMessage
from messages.Time import Time
from helpers import (
    get_airways_between_fixs,
    airways_to_legs,
    get_sid_approaches_by_airport_ident,
    get_star_approaches_by_airport_ident,
    get_approach_approaches_by_airport_ident
)
from utils.leg import Leg
from utils.physics import Speed
from db.models import Approach


class Flightplan:
    def __init__(
        self,
        flight_rules: str,
        cruise_speed: Speed,
        departure_airport: str,
        cruise_altitude: Distance,  # F200 => 200
        arrival_airport: str,
        route: str,
        aircraft_icao: str,
        hours_en_route: int = 1,
        minutes_enroute: int = 55,
        hours_fuel: int = 3,
        minutes_fuel: int = 30,
        type_of_flight: Literal['S', 'N', 'G', 'M', 'X'] = 'S',
        estimated_departure: Time = Time(13, 35),
        actual_departure: Time = Time(13, 35),
        alternate_airport: str = '',
        remarks: str = '',
        number_of_aircraft: int = 1,
        wake_turbulence_category: str = 'M',
        equipment: str = '',
        transponder_types: str = 'LB1',
    ):
        self.flight_rules = flight_rules
        self.type_of_flight = type_of_flight
        self.aircraft_icao = aircraft_icao
        self.cruise_speed = cruise_speed
        self.departure_airport = departure_airport
        self.estimated_departure = estimated_departure
        self.actual_departure = actual_departure
        self.cruise_altitude = cruise_altitude
        self.arrival_airport = arrival_airport
        self.hours_en_route = hours_en_route
        self.minutes_enroute = minutes_enroute
        self.hours_fuel = hours_fuel
        self.minutes_fuel = minutes_fuel
        self.alternate_airport = alternate_airport
        self.remarks = remarks
        self.route = route
        self.number_of_aircraft = number_of_aircraft
        self.wake_turbulence_category = wake_turbulence_category
        self.equipment = equipment
        self.transponder_types = transponder_types

    @property
    def aircraft_type(self):
        return f'{self.number_of_aircraft}/{self.aircraft_icao}/{self.wake_turbulence_category}-{self.equipment}/{self.transponder_types}'

    def get_legs(self, start_leg: Leg):
        legs = [start_leg]
        items = self.route.split(' ')
        items.pop(0)  # popup sid fix
        while len(items) != 0:
            airway_name = items.pop(0)
            to_fix_name = items.pop(0)
            new_airways = get_airways_between_fixs(
                airway_name, legs[-1].fix, to_fix_name)
            new_legs = airways_to_legs(new_airways)
            extended_legs = new_legs[1:]
            legs.extend(extended_legs)
        return legs

    def get_message(self, source: str, destination: str):
        return FlightplanMessage(
            source=source,
            destination=destination,
            flight_rules=self.flight_rules,
            type_of_flight=self.type_of_flight,
            aircraft_type=self.aircraft_type,
            cruise_speed=f"N{str(int(self.cruise_speed.mph)).zfill(4)}",
            departure_airport=self.departure_airport,
            estimated_departure=self.estimated_departure,
            actual_departure=self.actual_departure,
            cruise_alt=f"F{str(int(self.cruise_altitude.feet))[:-2].zfill(3)}",
            arrival_airport=self.arrival_airport,
            hours_en_route=self.hours_en_route,
            minutes_enroute=self.minutes_enroute,
            hours_fuel=self.hours_fuel,
            minutes_fuel=self.minutes_fuel,
            alternate_airport=self.alternate_airport,
            remarks=self.remarks,
            route=self.route,
        )

    def get_usable_sids(self):
        sid_approaches = get_sid_approaches_by_airport_ident(
            self.departure_airport)
        end_leg_waypoint_ident = self.route.split(' ')[0]
        return [
            sa for sa in sid_approaches if sa.approach_legs[-1].fix_ident == end_leg_waypoint_ident
        ]

    def get_usable_stars(self):
        star_approaches = get_star_approaches_by_airport_ident(
            self.arrival_airport)
        start_leg_waypoint_ident = self.route.split(' ')[-1]
        return [
            sa for sa in star_approaches if sa.approach_legs[0].fix_ident == start_leg_waypoint_ident
        ]

    def get_usable_approaches(self, star_approach: Approach | None = None):
        start_leg_waypoint_ident = self.route.split(
            ' ')[-1] if star_approach is None else star_approach.approach_legs[-1].fix_ident
        approach_approaches = get_approach_approaches_by_airport_ident(
            self.arrival_airport)

        usable_approaches: list[Approach] = []
        for aa in approach_approaches:
            if aa.approach_legs[0].fix_ident == start_leg_waypoint_ident:
                usable_approaches.append(aa)
            else:
                for t in aa.transitions:
                    if t.fix_ident == start_leg_waypoint_ident:
                        usable_approaches.append(aa)
        return usable_approaches
