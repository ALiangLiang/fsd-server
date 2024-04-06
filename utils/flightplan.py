from messages.FlightplanMessage import FlightplanMessage
from messages.Time import Time
from helpers import get_airways_between_fixs, airways_to_legs
from utils.leg import Leg
from utils.physics import Speed


class Flightplan:
    def __init__(
        self,
        flight_rules: str,
        cruise_speed: Speed,
        departure_airport: str,
        cruise_altitude: int,  # F200 => 200
        arrival_airport: str,
        route: str,
        hours_en_route: int = 1,
        minutes_enroute: int = 55,
        hours_fuel: int = 3,
        minutes_fuel: int = 30,
        type_of_flight: str = 'I',
        aircraft_type: str = 'S',
        estimated_departure: Time = Time(13, 35),
        actual_departure: Time = Time(13, 35),
        alternate_airport: str = '',
        remarks: str = '',
    ):
        self.flight_rules = flight_rules
        self.type_of_flight = type_of_flight
        self.aircraft_type = aircraft_type
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

    def get_legs(self, start_leg: Leg):
        legs = [start_leg]
        items = self.route.split(' ')
        items.pop(0)  # popup sid fix
        while len(items) != 0:
            airway_name = items.pop(0)
            to_fix_name = items.pop(0)
            new_airways = get_airways_between_fixs(
                airway_name, legs[-1].waypoint, to_fix_name)
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
            cruise_speed=f"N{str(self.cruise_speed.mph).zfill(4)}",
            departure_airport=self.departure_airport,
            estimated_departure=self.estimated_departure,
            actual_departure=self.actual_departure,
            cruise_alt=f"F{str(self.cruise_altitude).zfill(3)}",
            arrival_airport=self.arrival_airport,
            hours_en_route=self.hours_en_route,
            minutes_enroute=self.minutes_enroute,
            hours_fuel=self.hours_fuel,
            minutes_fuel=self.minutes_fuel,
            alternate_airport=self.alternate_airport,
            remarks=self.remarks,
            route=self.route
        )
