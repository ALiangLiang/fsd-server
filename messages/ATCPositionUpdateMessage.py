from messages.IMessage import IMessage
from messages.Position import Position


class ATCPositionUpdateMessage(IMessage):
    command = '%'

    def __init__(self, callsign: str, frequency: int, facility: int, visibility: int, rating: int, position: Position):
        super().__init__()
        self.callsign = callsign
        self.frequency = frequency
        self.facility = facility
        self.visibility = visibility
        self.rating = rating
        self.position = position

    @classmethod
    def parse_raw_message(cls, raw_message):
        callsign, frequency, facility, visibility, rating, latitude, longitude, elevation = \
            raw_message[len(cls.command):].split(':')
        position = Position(float(latitude), float(longitude))
        position.altitude_ = elevation
        return cls(callsign, int(frequency), int(facility), int(visibility), int(rating or 0), position)

    def __str__(self):
        return self.command + ':'.join([
            self.callsign,
            self.frequency,
            self.facility,
            self.visibility,
            self.rating,
            str(self.position),
            self.position.altitude_
        ])
