from datetime import timedelta
from enum import Enum
from logging import getLogger
from math import isclose, radians, tan

from geopy.distance import Distance

from db.models import TaxiPath, Parking, RunwayEnd
from utils.geo import (
    get_bearing_distance,
    fix_radial_distance,
)
from utils.flightplan import Flightplan
from utils.leg import Leg
from utils.unit import lbs_to_kg
from utils.physics import get_acceleration_by_newton_2th, Speed
from helpers import get_displacement_by_seconds, get_fix_by_ident
from messages.PilotPositionUpdateMessage import TransponderMode
from messages.Position import Position
from messages.TextMessage import TextMessage
from aircrafts.aircraft import Aircraft

logger = getLogger(__name__)


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


class AircraftStatus(Enum):
    NOT_DELIVERED = 0
    DELIVERED = 1  # delivered but not approved pushback and startup
    APPROVED_PUSHBACK_STARTUP = 2  # approved pushback and startup
    APPROVED_TAXI_TO_RWY = 3  # approved taxi
    LINEUP_WAIT = 4  # cleared for takeoff
    CLEARED_TAKEOFF = 5  # cleared for takeoff
    CLEARED_LAND = 6  # cleared to land
    MISSED_APPROACH = 7  # missed approach
    VACATE_RUNWAY = 8  # vacate runway
    APPROVED_TAXI_TO_BAY = 9  # approved taxi to bay


class BotAircraft(Aircraft):
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
    taxi_path: list[TaxiPath]
    status: AircraftStatus

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
        speed_limit: Speed | None = None,
        target_altitude: Distance | None = None,
    ):
        super().__init__(
            callsign=callsign,
            position=position,
            speed=speed,
            is_on_ground=is_on_ground,
            squawk_code=squawk_code,
            transponder_mode=transponder_mode,
            flightplan=flightplan,
        )
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

        self.legs = combine_legs(
            sid_legs,
            enroute_legs,
            star_legs,
            approach_legs
        )
        self.position = position or self.legs[0].position.copy()
        self.sid_legs = sid_legs
        self.star_legs = star_legs
        self.approach_legs = approach_legs
        # top of descent. Distance to the leg
        self.tod: tuple[Distance, Leg] | None = None
        self.speed_limit = speed_limit
        self.target_altitude = target_altitude
        self.pushback_path: list[Position] = []
        self.taxi_path: list[Position] = []
        self.vacatable_taxi_paths: dict[str, list[Position]] = {}
        self.departure_path: list[Position] = []
        self.expect_runway_end: RunwayEnd | None = None
        self.parking: Parking | None = None
        self.status = AircraftStatus.NOT_DELIVERED
        self.is_intercept_ils = False

        self.takeoff_acceleration = get_acceleration_by_newton_2th(
            lbs_to_kg(self.to1),
            self.mtow,
            self.drag_coefficient
        )
        self.decend_acceleration = get_acceleration_by_newton_2th(
            0,
            self.mtow,
            self.drag_coefficient
        )
        self.retard_acceleration = get_acceleration_by_newton_2th(
            -lbs_to_kg(self.to2),
            self.mtow,
            self.drag_coefficient
        )
        self.on_pushback_completed = lambda: None

    @property
    def is_no_more_legs(self):
        return len(self.legs) == 0

    def set_parking(self, parking: Parking | None):
        self.parking = parking
        return self

    def set_expect_runway_end(self, runway_end: RunwayEnd | None):
        self.expect_runway_end = runway_end
        return self

    def set_status(self, status: AircraftStatus):
        self.status = status
        return self

    def start_pushback(self, pushback_path: list[Position] | None = None):
        if pushback_path is not None:
            self.pushback_path = pushback_path
        self.status = AircraftStatus.APPROVED_PUSHBACK_STARTUP
        return self

    def start_taxi(self, taxi_path: list[Position] | None = None):
        if taxi_path is not None:
            self.taxi_path += taxi_path
        self.status = AircraftStatus.APPROVED_TAXI_TO_RWY
        return self

    def set_departure_path(self, departure_path: list[Position]):
        self.departure_path = departure_path
        return self

    def start_lineup_wait(self, departure_path: list[Position] | None = None):
        if departure_path is not None:
            self.departure_path = departure_path
        self.status = AircraftStatus.LINEUP_WAIT
        return self

    def start_departure(self, departure_path: list[Position] | None = None):
        if departure_path is not None:
            self.departure_path = departure_path
        self.status = AircraftStatus.CLEARED_TAKEOFF
        return self

    def start_missed_approach(self):
        self.status = AircraftStatus.MISSED_APPROACH
        return self

    def start_land(self, vacated_taxi_path: list[Position] | None = None):
        if vacated_taxi_path is not None:
            self.taxi_path = vacated_taxi_path
        self.status = AircraftStatus.CLEARED_LAND
        return self

    def set_speed_limit(self, speed_limit: Speed | None):
        self.speed_limit = speed_limit
        return self

    def set_target_altitude(self, target_altitude: Distance | None):
        self.target_altitude = target_altitude
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

    def set_approach_legs(self, approach_legs: list[Leg]):
        old_legs = combine_legs(self.star_legs, self.approach_legs)
        self.remove_continuously_end_legs(old_legs)

        self.approach_legs = approach_legs
        self.legs = approach_legs
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

    def pushback(self, after_time: timedelta):
        if self.position is None:
            return

        if len(self.pushback_path) == 0:
            return

        bearing, distance_to_leg = get_bearing_distance(
            self.position,
            self.pushback_path[0]
        )
        self.heading = bearing
        self.speed = Speed(knots=5)

        distance: Distance = self.speed * after_time
        if distance_to_leg < distance:
            self.pushback_path.pop(0)

        new_position = fix_radial_distance(self.position, bearing, distance)
        self.position.set_coordinates(
            new_position.latitude,
            new_position.longitude,
        )

    def taxi_to_hold_short(self, after_time: timedelta, speed: Speed = Speed(knots=30)):
        if self.position is None:
            return

        if len(self.taxi_path) == 0:
            return

        bearing, distance_to_leg = get_bearing_distance(
            self.position,
            self.taxi_path[0]
        )
        self.heading = bearing
        self.speed = speed

        distance: Distance = min(
            self.speed * after_time,
            distance_to_leg
        )
        if distance_to_leg <= distance:
            self.position.set_coordinates(
                self.taxi_path[0].latitude,
                self.taxi_path[0].longitude,
            )
            self.taxi_path.pop(0)
            return

        new_position = fix_radial_distance(self.position, bearing, distance)
        self.position.set_coordinates(
            new_position.latitude,
            new_position.longitude,
        )

    def taxi_to_start_n_takeoff(self, after_time: timedelta):
        if self.position is None:
            return

        # not taxi to hold short. keep taxiing
        if len(self.taxi_path) != 0:
            self.taxi_to_hold_short(after_time)
            return

        if len(self.departure_path) != 0:
            self.taxi_to_start(after_time)
        elif self.is_intercept_ils:
            self.ils_approach(after_time)
        else:
            self.takeoff(after_time)

    def taxi_to_start(self, after_time: timedelta):
        if self.position is None:
            return

        # not taxi to hold short. keep taxiing
        if len(self.taxi_path) != 0:
            self.taxi_to_hold_short(after_time)
            return

        if len(self.departure_path) == 0:
            return

        bearing, distance_to_leg = get_bearing_distance(
            self.position,
            self.departure_path[0]
        )
        self.heading = bearing
        self.speed = Speed(knots=15)

        distance: Distance = min(
            self.speed * after_time,
            distance_to_leg
        )
        if distance_to_leg <= distance:
            self.departure_path.pop(0)

        new_position = fix_radial_distance(self.position, bearing, distance)
        self.position.set_coordinates(
            new_position.latitude,
            new_position.longitude,
        )

    def update_speed(self, after_time: timedelta, flightplan: Flightplan, position: Position):
        speed_limit = flightplan.cruise_speed if self.speed_limit is None else self.speed_limit
        if position.altitude_ < Distance(feet=10000):
            # if altitude below 10000ft, speed limit to 250 knots
            speed_limit = min(
                speed_limit,
                Speed(knots=240)
            )
        distance = Distance(nautical=0)
        if isclose(self.speed.knots, speed_limit.knots, abs_tol=2):
            distance = self.speed * after_time
        if self.speed < speed_limit:
            self.speed += self.takeoff_acceleration * after_time
            distance = get_displacement_by_seconds(
                self.takeoff_acceleration,
                after_time,
                self.speed
            )
        elif self.speed > speed_limit:
            if not self.is_on_ground:
                self.speed += self.decend_acceleration * after_time
                if self.speed < speed_limit:
                    self.speed = speed_limit
                distance = get_displacement_by_seconds(
                    self.decend_acceleration,
                    after_time,
                    self.speed
                )
            else:
                self.speed += self.retard_acceleration * after_time
                if self.speed < speed_limit:
                    self.speed = speed_limit
                distance = get_displacement_by_seconds(
                    self.decend_acceleration,
                    after_time,
                    self.speed
                )
        return distance

    def takeoff(self, after_time: timedelta):
        if self.flightplan is None or self.position is None:
            return

        # keep taxiing after clear for takeoff
        if len(self.taxi_path) != 0:
            self.taxi_to_hold_short(after_time)
            return

        target_leg = self.legs[0] if len(self.legs) > 0 else None

        # update limits
        if target_leg is not None:
            if target_leg.max_altitude_limit is not None and self.position.altitude_ > target_leg.max_altitude_limit:
                self.set_target_altitude(target_leg.max_altitude_limit)
            if target_leg.min_altitude_limit is not None and self.position.altitude_ < target_leg.min_altitude_limit:
                self.set_target_altitude(target_leg.min_altitude_limit)
            if target_leg.speed_limit is not None and self.speed > target_leg.speed_limit:
                self.set_speed_limit(target_leg.speed_limit)

        bearing, distance_to_leg = self.heading, Distance(nautical=999999)
        if target_leg is not None:
            bearing, distance_to_leg = get_bearing_distance(
                self.position,
                target_leg.position
            )

            # intercept ILS
            if target_leg.glide_slope_angle is not None:
                self.is_intercept_ils = True

        # turn
        self.heading = bearing
        # if distance_to_leg < Distance(nautical=5):
        #     if bearing > self.heading:  # turn right
        #         self.heading = min(
        #             # 4 degrees per second
        #             self.heading + Bearing(4) * after_time.total_seconds(),
        #             self.heading
        #         )
        #     else:  # turn left
        #         self.heading = max(
        #             # 4 degrees per second
        #             self.heading - Bearing(4) * after_time.total_seconds(),
        #             self.heading
        #         )

        # if altitude below 10000ft, speed limit to 250 knots
        if self.position.altitude_ < Distance(feet=10000):
            self.speed = min(
                self.speed,
                Speed(knots=250)
            )

        if self.is_on_ground is True:
            if not self.is_no_more_legs:
                if self.speed > self.vr:
                    # airborne
                    self.is_on_ground = False
            else:
                # landed
                self.set_speed_limit(Speed(knots=30))
                if self.speed < Speed(knots=60) and self.status == AircraftStatus.CLEARED_LAND:
                    self.status = AircraftStatus.VACATE_RUNWAY

                    if len(self.taxi_path) == 0:
                        vacatable_taxi_paths = []
                        for taxi_path in self.vacatable_taxi_paths.values():
                            bearing, distance_to_leg = get_bearing_distance(
                                self.position,
                                taxi_path[0]
                            )
                            if isclose(self.heading.degrees, bearing.degrees, abs_tol=60):
                                vacatable_taxi_paths.append(
                                    (taxi_path, distance_to_leg))
                        if len(vacatable_taxi_paths) != 0:
                            self.taxi_path = min(
                                vacatable_taxi_paths,
                                key=lambda x: x[1]
                            )[0]

        # update altitude
        if self.is_on_ground is False and self.position.altitude_ is not None:
            if self.target_altitude is None:
                # keep cruise altitude
                roc = self.climb_roc
                if self.position.altitude_ < Distance(feet=2500):
                    roc = Speed(fpm=5000)
                elif self.position.altitude_ < Distance(feet=10000):
                    roc = Speed(fpm=2500)
                if self.position.altitude_ < self.flightplan.cruise_altitude:
                    added_altitude = min(
                        roc * after_time,
                        self.flightplan.cruise_altitude - self.position.altitude_
                    )
                    self.position.add_altitude(added_altitude)
            # 100ft tolerance
            elif not isclose(self.position.altitude_.feet, self.target_altitude.feet, abs_tol=100):
                if self.position.altitude_ < self.target_altitude:
                    self.position.add_altitude(
                        min(
                            self.climb_roc * after_time,
                            self.target_altitude - self.position.altitude_
                        )
                    )
                elif self.position.altitude_ > self.target_altitude:
                    self.position.add_altitude(
                        min(
                            self.descent_roc * after_time,
                            self.position.altitude_ - self.target_altitude
                        )
                    )
            else:
                self.position.set_altitude(self.target_altitude)
            # check is touch down
            if target_leg is None and self.position.altitude_ <= self.target_altitude:
                self.is_on_ground = True
                self.position.set_altitude(self.target_altitude)
                self.set_speed_limit(Speed(knots=0))

        distance = self.update_speed(
            after_time,
            self.flightplan,
            self.position
        )

        if distance_to_leg < distance:
            if target_leg.max_altitude_limit is not None or target_leg.min_altitude_limit is not None:
                altitude = self.position.altitude_
                self.position.set_altitude(
                    max(
                        target_leg.min_altitude_limit or Distance(feet=0),
                        min(altitude, target_leg.max_altitude_limit or Distance(
                            feet=999999))
                    )
                )
            if target_leg.speed_limit is not None and self.speed > target_leg.speed_limit:
                self.set_speed(target_leg.speed_limit)

            self.to_next_leg()

        new_position = fix_radial_distance(self.position, bearing, distance)
        self.position.set_coordinates(
            new_position.latitude,
            new_position.longitude,
        )

    def ils_approach(self, after_time: timedelta):
        # If intercepted ILS, should has expect runway end
        if self.expect_runway_end is None:
            return

        loc_line = self.expect_runway_end.loc_line
        touch_down_position = self.expect_runway_end.touch_down_position
        if loc_line is None or touch_down_position is None:
            raise Exception('The runway end doesn\'t equip ILS.')
        if self.position is None or self.position.altitude_ is None:
            raise Exception('The aircraft doesn\'t have position or altitude.')

        point = loc_line.project_point([
            self.position.longitude,
            self.position.latitude,
        ])
        self.position.set_coordinates(
            point[1],
            point[0],
        )

        distance: Distance = self.speed * after_time
        bearing, distance_to_leg = get_bearing_distance(
            self.position,
            touch_down_position
        )

        target_leg = self.legs[0]
        radius = radians(abs(target_leg.glide_slope_angle))
        altitude_to_ground = distance_to_leg * tan(radius)
        if altitude_to_ground.feet < 100 and self.status != AircraftStatus.CLEARED_LAND:
            # go around
            pass

        altitude = altitude_to_ground + touch_down_position.altitude_
        self.position.set_altitude(altitude)

        new_position = fix_radial_distance(self.position, bearing, distance)
        self.position.set_coordinates(
            new_position.latitude,
            new_position.longitude,
        )

        # touch down
        if distance > distance_to_leg:
            self.position = touch_down_position.copy()
            self.is_intercept_ils = False
            self.is_on_ground = True
            self.legs = []

    def vacate_runway(self, after_time: timedelta):
        self.taxi_to_hold_short(after_time)

    # TODO: calculate TOD
    # TODO: adjust roc by leg restriction
    # TODO: support smooth turn
    def update_status(self, after_time: timedelta):
        if self.status == AircraftStatus.APPROVED_PUSHBACK_STARTUP:
            self.pushback(after_time)
        elif self.status == AircraftStatus.APPROVED_TAXI_TO_RWY:
            self.taxi_to_hold_short(after_time)
        elif self.status == AircraftStatus.LINEUP_WAIT:
            self.taxi_to_start(after_time)
        elif self.status == AircraftStatus.CLEARED_TAKEOFF:
            self.taxi_to_start_n_takeoff(after_time)
        elif self.status == AircraftStatus.CLEARED_LAND:
            self.taxi_to_start_n_takeoff(after_time)
        elif self.status == AircraftStatus.VACATE_RUNWAY:
            self.vacate_runway(after_time)

    def get_text_message(self, destination: str, text: str):
        return TextMessage(self.callsign, destination, text)

    def radio_check(self, destination: str):
        return self.get_text_message(destination, f'Hello, {self.callsign} radio check')

    def radio_check_atc(self, destination: str):
        return self.get_text_message(destination, 'Read you 5 too')

    def request_delivery(self, destination: str):
        if self.flightplan is None:
            return None

        flight_level_str = 'FL' + normalize_flight_level(
            self.flightplan.cruise_altitude.feets // 100)
        flight_rule_str = 'IFR' if self.flightplan.flight_rules == 'I' else 'VFR'
        # TODO: dynamic information number
        information = 'A'
        return self.get_text_message(
            destination,
            f'{self.callsign} request {flight_rule_str} clearance to {self.flightplan.arrival_airport}, {flight_level_str}, information {information}'
        )
