from datetime import datetime

from geopy.distance import Distance

from utils.geo import (
    get_bearing_distance,
    fix_radial_distance,
)
from utils.flightplan import Flightplan
from utils.leg import Leg
from utils.unit import lbs_to_kg
from utils.physics import get_acceleration_by_newton_2th, Speed
from helpers import get_displacement_by_seconds, get_fix_by_ident
from messages.PilotPositionUpdateMessage import PilotPositionUpdateMessage, TransponderMode
from messages.Position import Position

PRESSURE_DELTA = -1573


def normalize_flight_level(flight_level: int):
    return str(flight_level).zfill(3)


def normalize_cruise_speed(flight_level: int):
    return str(flight_level).zfill(4)


def combine_legs(*legs_list: list[Leg]):
    legs: list[Leg] = []
    for legs_ in legs_list:
        if len(legs) == 0:
            legs += legs_
        elif len(legs_) > 0:
            legs += legs_[1:] if legs[-1].ident == legs_[0].ident else legs_
    return legs

# def combine_legs(
#     sid_legs: list[Leg],
#     enroute_legs: list[Leg],
#     star_legs: list[Leg],
#     approach_legs: list[Leg]
# ):
#     # prevent duplicate leg between legs
#     legs: list[Leg] = [*sid_legs]
#     if len(legs) == 0:
#         legs += enroute_legs
#     elif len(enroute_legs) > 0:
#         legs += enroute_legs[1:] if legs[-1].ident == enroute_legs[0].ident else enroute_legs
#     if len(legs) == 0:
#         legs += star_legs
#     elif len(star_legs) > 0:
#         legs += star_legs[1:] if legs[-1].ident == star_legs[0].ident else star_legs
#     if len(legs) == 0:
#         legs += approach_legs
#     elif len(approach_legs) > 0:
#         legs += approach_legs[1:] if legs[-1].ident == approach_legs[0].ident else approach_legs
#     return legs


class Aircraft:
    icao_name: str
    type: str
    mtow: int
    to0: int
    to1: int
    to2: int
    climb_roc: Speed
    descent_roc: Speed
    drag_coefficient: float
    aircraft_type: str
    vr: Speed

    def __init__(
        self,
        callsign: str,
        position: Position | None = None,
        speed: Speed = Speed(0),
        is_on_ground: bool = True,
        squawk_code: str = '2000',
        transponder_mode: TransponderMode = TransponderMode.MODE_C,
        flightplan: Flightplan | None = None,
        sid_legs: list[Leg] = [],
        # if not provided, will use flightplan
        enroute_legs: list[Leg] | None = None,
        star_legs: list[Leg] = [],
        approach_legs: list[Leg] = [],
    ):
        if enroute_legs is None:
            if len(sid_legs) == 0:
                if flightplan is None:
                    enroute_legs = []
                else:
                    # guess enroute legs
                    usable_sids = flightplan.get_usable_sids()
                    if len(usable_sids) == 0:
                        enroute_legs = []
                    else:
                        sid_end_approach_leg = usable_sids[0].approach_legs[-1]
                        fix = get_fix_by_ident(
                            sid_end_approach_leg.fix_ident, sid_end_approach_leg.fix_region)
                        sid_end_leg = Leg.from_procedure_leg(
                            sid_end_approach_leg,
                            fix
                        )
                        enroute_legs = flightplan.get_legs(sid_end_leg)
            else:
                enroute_legs = flightplan.get_legs(
                    sid_legs[-1]) if (len(sid_legs) > 0 and flightplan is not None) else []

        self.flightplan = flightplan
        self.legs = combine_legs(
            sid_legs,
            enroute_legs,
            star_legs,
            approach_legs
        )
        self.callsign = callsign
        self.speed = speed
        self.position = position or self.legs[0].position.copy()
        self.is_on_ground = is_on_ground
        self.transponder_mode = transponder_mode
        self.squawk_code = squawk_code
        self.sid_legs = sid_legs
        self.star_legs = star_legs
        self.approach_legs = approach_legs

        self.takeoff_acceleration = get_acceleration_by_newton_2th(
            lbs_to_kg(self.to1),
            self.mtow,
            self.drag_coefficient
        )
        self.pitch = 0
        self.bank = 0
        self.heading = 0
        self._is_pause = False
        self._last_send_position_time = datetime.now()

    def set_position(self, position: Position):
        self.position = position
        return self

    def set_sid_legs(self, sid_legs: list[Leg]):
        self.sid_legs = sid_legs
        self.legs = combine_legs(
            sid_legs,
            self.flightplan.get_legs(
                sid_legs[-1]) if self.flightplan is not None else [],
            self.star_legs,
            self.approach_legs
        )
        return self

    def set_star_n_approach_legs(self, star_legs: list[Leg], approach_legs: list[Leg]):
        old_legs = combine_legs(self.star_legs, self.approach_legs)
        self.remove_continuously_end_legs(old_legs)

        self.star_legs = star_legs
        self.approach_legs = approach_legs
        self.legs = combine_legs(
            self.sid_legs,
            self.flightplan.get_legs(
                self.sid_legs[-1]) if self.flightplan is not None else [],
            star_legs,
            approach_legs
        )
        return self

    def remove_continuously_end_legs(self, legs: list[Leg]):
        is_matched = False
        for leg in reversed(legs):
            if self.legs[-1] != leg:
                is_matched = False
                break
            is_matched = True
        if is_matched:
            self.legs = self.legs[:-len(legs)]

    def direct_to_leg(self, leg: Leg):
        new_legs = [*self.legs]
        while new_legs.pop(0) != leg:
            pass
        if len(new_legs) == 0:
            return
        self.legs = new_legs

    def to_next_leg(self):
        self.legs.pop(0)

    # TODO: decend
    # TODO: brake after landed
    # TODO: shutdown after stoped
    # TODO: adjust roc by leg restriction
    # TODO: support smooth turn
    def update_status(self):
        if len(self.legs) == 0:
            return

        bearing, distance_to_leg = get_bearing_distance(
            self.position,
            self.legs[0].position
        )
        self.heading = bearing

        # updat speed
        now = datetime.now()
        time_diff = now - self._last_send_position_time
        self._last_send_position_time = now
        if self.speed < self.flightplan.cruise_speed:
            distance = get_displacement_by_seconds(
                self.takeoff_acceleration,
                time_diff,
                self.speed
            )
            self.speed += self.takeoff_acceleration * time_diff
        else:
            self.speed = self.flightplan.cruise_speed
            distance: Distance = self.speed * time_diff

        # update altitude
        if self.speed > self.vr:
            # airborne
            self.is_on_ground = False

            roc = self.climb_roc
            if self.position.altitude_ < 2500:
                roc = Speed(fpm=5000)
            elif self.position.altitude_ < 10000:
                roc = Speed(fpm=2500)
            elif self.position.altitude_ < self.flightplan.cruise_altitude:
                added_altitude = max(
                    (roc * time_diff),
                    Distance(feets=self.flightplan.cruise_altitude -
                             self.position.altitude_)
                )
                self.position.add_altitude(added_altitude.feet)

        #     if is_send_airborne_msg == False and self.position.altitude_ > 500:
        #         text_message = TextMessage(
        #             self.callsign,
        #             frequency_to_abbr(FREQUENCE),
        #             'Taipei Tower, Good evening, ' + AC_CALLSIGN + ', airborne'
        #         )
        #         await send(client_socket, str(text_message))
        #         is_send_airborne_msg = True

        print('move meters:', distance.meters, ', speed:', self.speed.knots, 'knots,',
              'altitude:', self.position.altitude_, 'feets,', 'on ground:', self.is_on_ground)

        print('Left legs:', [leg.ident for leg in self.legs])

        if distance_to_leg < distance:
            self.to_next_leg()

        new_position = fix_radial_distance(self.position, bearing, distance)
        self.position.set_coordinates(
            new_position.latitude,
            new_position.longitude,
        )

    def get_position_update_message(self):
        self.update_status()

        return PilotPositionUpdateMessage(
            callsign=self.callsign,
            ident=self.transponder_mode,
            squawk_code=self.squawk_code,
            rating='4',
            position=self.position,
            altitude=self.position.altitude_,
            speed=self.speed,
            pbh=(self.pitch, self.bank, self.heading, self.is_on_ground),
            pressure_delta=PRESSURE_DELTA
        )

    def get_flightplan_message(self, destination_callsign: str):
        if self.flightplan is None:
            return None
        return self.flightplan.get_message(
            source=self.callsign,
            destination=destination_callsign,
        )
