from messages.IMessage import IMessage


class PilotPositionUpdateMessage(IMessage):
    command = '@'

    def __init__(self, callsign, ident, squawk_code, rating, position, altitude, speed, pbh, pressure_delta):
        super().__init__()
        self.callsign = callsign
        self.ident = ident
        self.squawk_code = squawk_code
        self.rating = rating
        self.position = position
        self.altitude = altitude
        self.speed = speed
        self.pbh = pbh
        self.pressure_delta = pressure_delta

    @staticmethod
    def parse_raw_message(raw_message):
        raise NotImplementedError('Not implemented')

    def tuple_to_pbh(self, pitch, bank, heading, on_ground):
        def scale(value):
            return int((value + 360) % 360 * 2.8444444444444444444444444444)

        num = 1023
        return (int(scale(pitch) & num)) \
            + (int(scale(bank) & num) << 10) \
            + (int(scale(heading) & num) << 21) \
            + (2 if on_ground else 0)

    @staticmethod
    def pbh_to_tuple(cls, value):
        def unscale(value):
            return value / 2.8444444444444444444444444444

        num = 1023
        return {
            'Pitch': unscale((value >> 22) & 0xFFFF),
            'Bank': unscale((value >> 12) & num),
            'Heading': unscale((value >> 2) & num),
            'OnGround': (value & 2) == 2
        }

    def __str__(self):
        return self.command + ":".join([
            self.ident,
            self.callsign,
            self.squawk_code,
            self.rating,
            str(self.position),
            str(self.altitude),
            str(self.speed),
            # str(self.tuple_to_pbh(*self.pbh)),
            '4261414408',  # Placeholder for tupleToPBH result, since the conversion logic is commented out
            str(self.pressure_delta)
        ])
