from datetime import datetime
from enum import Enum

from geopy.distance import Distance

from utils.geo import (
    get_bearing_distance,
    fix_radial_distance,
)
from utils.flightplan import Flightplan
from utils.leg import Leg
from utils.unit import lbs_to_kg
from utils.physics import get_acceleration_by_newton_2th, Speed
from helpers import get_displacement_by_seconds
from messages.PilotPositionUpdateMessage import PilotPositionUpdateMessage, TransponderMode
from messages.Position import Position

PRESSURE_DELTA = -1573


def normalize_flight_level(flight_level: int):
    return str(flight_level).zfill(3)


def normalize_cruise_speed(flight_level: int):
    return str(flight_level).zfill(4)


def combine_legs(
    sid_legs: list[Leg],
    enroute_legs: list[Leg],
    star_legs: list[Leg],
    approach_legs: list[Leg]
):
    # prevent duplicate leg between legs
    legs: list[Leg] = [*sid_legs]
    if len(legs) == 0:
        legs += enroute_legs
    elif len(enroute_legs) > 0:
        legs += enroute_legs[1:] if legs[-1].ident == enroute_legs[0].ident else enroute_legs
    if len(legs) == 0:
        legs += star_legs
    elif len(star_legs) > 0:
        legs += star_legs[1:] if legs[-1].ident == star_legs[0].ident else star_legs
    if len(legs) == 0:
        legs += approach_legs
    elif len(approach_legs) > 0:
        legs += approach_legs[1:] if legs[-1].ident == approach_legs[0].ident else approach_legs
    return legs


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
        position: Position,
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
        bearing = self.heading
        distance_to_leg = Distance(meters=1500)
        if len(self.legs) > 0:
            bearing, distance_to_leg = get_bearing_distance(
                self.position,
                self.legs[0].position
            )
        self.heading = bearing

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

        if self.speed > self.vr:
            # airborne
            self.is_on_ground = False

            roc = self.climb_roc
            if self.position.altitude_ < 2500:
                roc = Speed(fpm=5000)
            elif self.position.altitude_ < 10000:
                roc = Speed(fpm=2500)
            self.position.add_altitude((roc * time_diff).feet)

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

    # async def tick_move_aircraft(
    #     self,
    #     dep_airport: str,
    #     dep_runway: str,
    #     arr_airport: str,
    #     arr_runway: str,
    #     route_str: str,
    #     flight_level: int,
    #     cruise_speed: int,
    #     remark: str = '',
    #     vr: int = 145,  # kts
    # ):
    #     flight_level = normalize_flight_level(flight_level)
    #     cruise_speed = normalize_cruise_speed(cruise_speed)
    #     full_route_str = f"{dep_airport}/{dep_runway} N{cruise_speed}F{flight_level} {route_str} {arr_airport}/I{arr_runway}"
    #     legs = get_legs_by_route_str(full_route_str)
    #     pos = legs[0].position
    #     start_time = time.time()
    #     last_time = start_time
    #     last_speed = 0
    #     last_altitude = legs[0].position.altitude_ or 0
    #     is_send_airborne_msg = False
    #     is_send_flightplan = False
    #     is_on_ground = True
    #     current_leg_index = 0
    #     while self._is_pause == False:
    #         if is_send_flightplan == False and last_time - start_time > 3:
    #             await send_flight_plan(client_socket)
    #             is_send_flightplan = True

    #         bearing, distance_to_leg = get_bearing_distance(
    #             pos,
    #             legs[current_leg_index].position
    #         )
    #         now = time.time()
    #         time_diff = now - last_time
    #         last_time = now
    #         if last_speed < CRUISE_SPEED:
    #             distance = get_displacement_by_seconds(
    #                 TAKEOFF_ACCELERATION,
    #                 time_diff,
    #                 last_speed
    #             )
    #             last_speed += TAKEOFF_ACCELERATION * time_diff
    #         else:
    #             last_speed = CRUISE_SPEED
    #             distance = Distance(meters=last_speed * time_diff)

    #         if last_speed > vr:
    #             # airborne
    #             is_on_ground = False
    #             last_altitude += RoC * time_diff

    #             if is_send_airborne_msg == False and last_altitude > 500:
    #                 text_message = TextMessage(
    #                     AC_CALLSIGN,
    #                     frequency_to_abbr(FREQUENCE),
    #                     'Taipei Tower, Good evening, ' + AC_CALLSIGN + ', airborne'
    #                 )
    #                 await send(client_socket, str(text_message))
    #                 is_send_airborne_msg = True

    #         print('move meters:', distance.meters, 'speed:', last_speed,
    #               'altitude:', last_altitude, 'on ground:', is_on_ground)

    #         if distance_to_leg < distance:
    #             if current_leg_index == len(legs) - 1:
    #                 break
    #             current_leg_index += 1
    #             continue

    #         print('Next leg:', legs[current_leg_index].ident)

    #         pos = fix_radial_distance(pos, bearing, distance)

    #         message = PilotPositionUpdateMessage(
    #             AC_CALLSIGN,
    #             'N',
    #             SQUAWK_CODE,
    #             '4',
    #             pos,
    #             last_altitude,
    #             last_speed,
    #             (*PBH_TUPLE[:2], is_on_ground),
    #             PRESSURE_DELTA
    #         )
    #         await send(client_socket, str(message))
    #         time.sleep(2)
