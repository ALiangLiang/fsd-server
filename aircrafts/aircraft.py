from random import randint

from utils.bearing import Bearing
from utils.flightplan import Flightplan
from utils.physics import Speed
from messages.DeletePilotMessage import DeletePilotMessage
from messages.PilotPositionUpdateMessage import TransponderMode, PilotPositionUpdateMessage
from messages.Position import Position

PRESSURE_DELTA = randint(-1500, 1500)


class Aircraft:
    def __init__(
        self,
        callsign: str,
        position: Position | None = None,
        speed: Speed = Speed(0),
        is_on_ground: bool = True,
        squawk_code: str = '2000',
        transponder_mode: TransponderMode = TransponderMode.STANDBY,
        flightplan: Flightplan | None = None,
    ):
        self.callsign = callsign
        self.position = position
        self.speed = speed
        self.is_on_ground = is_on_ground
        self.squawk_code = squawk_code
        self.transponder_mode = transponder_mode
        self.flightplan = flightplan

        self.pitch = 0
        self.bank = 0
        self.heading = Bearing(0)
        self.is_flying = False

    def set_position(self, position: Position):
        self.position = position
        return self

    def set_squawk(self, squawk_code: str):
        self.squawk_code = squawk_code
        return self

    def set_transponder_mode_c(self):
        self.transponder_mode = TransponderMode.MODE_C
        return self

    def get_position_update_message(self):
        return PilotPositionUpdateMessage(
            callsign=self.callsign,
            ident=self.transponder_mode,
            squawk_code=self.squawk_code,
            rating='4',
            position=self.position,
            altitude=self.position.altitude_,
            speed=self.speed,
            pbh=(self.pitch, self.bank, self.heading.degrees, self.is_on_ground),
            pressure_delta=PRESSURE_DELTA
        )

    def get_flightplan_message(self, destination_callsign: str):
        if self.flightplan is None:
            return None
        return self.flightplan.get_message(
            source=self.callsign,
            destination=destination_callsign,
        )

    def get_delete_message(self):
        return DeletePilotMessage(self.callsign)
