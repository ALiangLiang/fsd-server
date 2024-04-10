from geopy.distance import Distance

from messages.IMessage import IMessage


class ClearedFlightlevelMessage(IMessage):
    command = '=F'

    def __init__(self, source: str, destination: str, pilot: str, flight_level: Distance | None):
        super().__init__()
        self.source = source
        self.destination = destination
        self.pilot = pilot
        self.flight_level = flight_level

    @classmethod
    def parse_raw_message(cls, raw_message):
        source, destination, pilot, flight_level_str = raw_message[len(
            cls.command):].split(':')
        flight_level = Distance(feet=int(flight_level_str)
                                * 100) if flight_level_str != '' else None
        return cls(source, destination, pilot, flight_level)

    def __str__(self):
        return self.command + ':'.join([
            self.source,
            self.destination,
            self.pilot,
            int(self.flight_level.feet) // 100 if self.flight_level is not None else '',
        ])
