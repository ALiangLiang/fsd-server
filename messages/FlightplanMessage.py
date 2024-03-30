from messages.IMessage import IMessage


class FlightplanMessage(IMessage):
    command = '$FP'

    def __init__(
        self,
        source,
        destination,
        flight_rules,
        type_of_flight,
        aircraft_type,
        cruise_speed,
        departure_airport,
        estimated_departure,
        actual_departure,
        cruise_alt,
        arrival_airport,
        hours_en_route,
        minites_enroute,
        hours_fuel,
        minutes_fuel,
        alternate_airport,
        remarks,
        route
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
        self.minutes_enroute = minites_enroute
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
