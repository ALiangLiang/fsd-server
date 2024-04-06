from enum import Enum

from messages.IMessage import IMessage
from messages.Position import Position
from utils.physics import Speed


class TransponderMode(Enum):
    STANDBY = 'S'
    MODE_C = 'N'
    SQUAWK_IDENT = 'Y'


class PilotPositionUpdateMessage(IMessage):
    command = '@'

    def __init__(
        self,
        callsign: str,
        ident: TransponderMode,
        squawk_code: str,
        rating: str,
        position: Position,
        altitude: float,
        speed: Speed,
        pbh: tuple[int, int, int, bool],
        pressure_delta: int
    ):
        super().__init__()
        self.callsign = callsign
        self.ident = ident  # S=Standby, N=Mode C, Y=Squawk ident
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

    def tuple_to_pbh(self):
        pitch, bank, heading, on_ground = self.pbh

        def scale(value: float):
            return int((value + 360) % 360 * (128 / 45))

        num = 1023
        return (int(scale(pitch) & num) << 22) \
            + (int(scale(bank) & num) << 12) \
            + (int(scale(heading) & num) << 2) \
            + (1 if on_ground else 0) << 1

    @classmethod
    def pbh_to_tuple(cls, value):
        def unscale(value):
            return value / (128 / 45)

        num = 1023
        return (
            unscale((value >> 22) & num),
            unscale((value >> 12) & num),
            unscale((value >> 2) & num),
            (value & 2) == 2
        )

    def __str__(self):
        return self.command + ":".join([
            self.ident.value,
            self.callsign,
            self.squawk_code,
            self.rating,
            str(self.position),
            str(int(self.altitude)),
            str(int(self.speed.knots)),
            str(self.tuple_to_pbh()),
            # '4261414408',  # Placeholder for tupleToPBH result, since the conversion logic is commented out
            str(self.pressure_delta)
        ])
