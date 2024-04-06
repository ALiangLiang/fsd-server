from messages.IMessage import IMessage
from messages.Time import Time


class FlightplanMessage(IMessage):
    command = '$FP'

    def __init__(
        self,
        source: str,
        destination: str,
        flight_rules: str,
        type_of_flight: str,
        aircraft_type: str,
        cruise_speed: str,
        departure_airport: str,
        estimated_departure: Time,
        actual_departure: Time,
        cruise_alt: str,
        arrival_airport: str,
        hours_en_route: int,
        minutes_enroute: int,
        hours_fuel: int,
        minutes_fuel: int,
        route: str,
        alternate_airport: str = '',
        remarks: str = '',
    ):
        super().__init__()
        self.source = source
        self.destination = destination
        self.flight_rules = flight_rules
        self.type_of_flight = type_of_flight
        self.aircraft_type = aircraft_type
        self.cruise_speed = cruise_speed
        self.departure_airport = departure_airport
        self.estimated_departure = estimated_departure
        self.actual_departure = actual_departure
        self.cruise_alt = cruise_alt
        self.arrival_airport = arrival_airport
        self.hours_en_route = hours_en_route
        self.minutes_enroute = minutes_enroute
        self.hours_fuel = hours_fuel
        self.minutes_fuel = minutes_fuel
        self.alternate_airport = alternate_airport
        self.remarks = remarks
        self.route = route

    @staticmethod
    def parse_raw_message(raw_message):
        raise NotImplementedError('Not implemented')

    def __str__(self):
        return self.command + ":".join([
            self.source,
            self.destination,
            self.flight_rules,
            self.aircraft_type,
            str(self.cruise_speed),
            self.departure_airport,
            str(self.estimated_departure),
            str(self.actual_departure),
            str(self.cruise_alt),
            self.arrival_airport,
            str(self.hours_en_route),
            str(self.minutes_enroute),
            str(self.hours_fuel),
            str(self.minutes_fuel),
            self.alternate_airport,
            self.remarks,
            self.route,
            self.type_of_flight,
            '0',
            ''
        ])
