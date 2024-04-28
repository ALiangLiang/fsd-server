import random
import logging
from datetime import timedelta

from geopy.distance import Distance

from aircrafts.b738 import B738
from utils.squawk_code import generate_taipei_fir_squawk_code
from utils.preset_flightplans import flightplans
from utils.flightplan import Flightplan
from utils.physics import Speed
from db.models import Parking
from helpers import fill_position_on_legs, get_start_leg, get_airport_by_ident, get_approach_by_id
from aircrafts.bot_aircraft import BotAircraft, TransponderMode, AircraftStatus

logger = logging.getLogger(__name__)

airline_icaos = ['CAL', 'EVA', 'SJX', 'TTW',
                 'CPA', 'FDX'] + ['VJC', 'CES', 'AMU', 'AIQ', 'THY']


class AircraftFactory:
    aircrafts: dict[str, BotAircraft] = {}

    def generate_callsign(self):
        def generate_random_callsign():
            return f'{random.choice(airline_icaos)}{random.randint(100, 999)}'
        callsign = generate_random_callsign()
        while self.aircrafts.get(callsign) is not None:
            callsign = generate_random_callsign()
        return callsign

    def generate_flightplan(self):
        return f'{random.choice(airline_icaos)}{random.randint(100, 999)}'

    def generate_w_random_situation(self, random_progress: bool = False):
        flightplan = random.choice(flightplans)
        callsign = self.generate_callsign()

        try:
            if flightplan.aircraft_icao == 'B738':
                aircraft = B738(
                    callsign=callsign,
                    flightplan=flightplan,
                    is_on_ground=True,
                    squawk_code=generate_taipei_fir_squawk_code(
                        flightplan.departure_airport,
                        flightplan.arrival_airport,
                        flightplan.flight_rules
                    )
                )
            else:
                return

            usable_sids = flightplan.get_usable_sids()
            used_sid = random.choice(usable_sids)
            aircraft.set_sid_legs(
                fill_position_on_legs(
                    used_sid.approach_legs,
                    flightplan.departure_airport
                )
            )
            aircraft.set_position(
                get_start_leg(used_sid.airport_ident,
                              used_sid.runway_name).position
            )

            usable_stars = flightplan.get_usable_stars()
            used_star = random.choice(usable_stars) if len(
                usable_stars) != 0 else None
            used_star_last_fix_ident = used_star.approach_legs[-1].fix_ident if used_star is not None else None
            usable_approaches = flightplan.get_usable_approaches(used_star)
            used_approach = random.choice(usable_approaches) if len(
                usable_approaches) != 0 else None
            usable_transitions = []
            if used_approach and (used_approach.approach_legs[0].fix_ident != used_star_last_fix_ident):
                usable_transitions = [
                    t for t in used_approach.transitions if t.fix_ident == used_star_last_fix_ident
                ]
            used_transition = None
            if len(usable_transitions) != 0:
                used_transition = random.choice(usable_transitions)

            approach_legs = used_approach.approach_legs if used_approach is not None else []
            not_missed_approach_legs = [
                al for al in approach_legs if al.is_missed == 0]
            aircraft.set_star_n_approach_legs(
                fill_position_on_legs(
                    used_star.approach_legs if used_star is not None else [],
                    flightplan.arrival_airport
                ),
                fill_position_on_legs(
                    (used_transition.transition_legs if used_transition is not None else []) +
                    not_missed_approach_legs,
                    flightplan.arrival_airport
                )
            )
            aircraft.set_expect_runway_end(used_approach.runway_end)

            if random_progress:
                online_time = random.randint(0, int(3600 / 2)) * 2
                for _ in range(0, online_time, 2):
                    if aircraft.is_no_more_legs:
                        return
                    aircraft.update_status(timedelta(seconds=2))

            self.aircrafts[callsign] = aircraft
            return aircraft

        except Exception as e:
            logger.exception(e)
            logger.debug(
                'Error occured on "%s %s %s"' % (
                    flightplan.departure_airport,
                    flightplan.route,
                    flightplan.arrival_airport
                )
            )
            return None

    def generate_on_parking(
        self,
        departure_airport_ident: str,
        callsign: str | None = None,
        flightplan: Flightplan | None = None,
        parking: Parking | None = None,
    ):
        airport = get_airport_by_ident(departure_airport_ident)
        if airport is None:
            raise Exception('Airport not found')

        if flightplan is None:
            candidate_flightplane = [fp for fp in flightplans if fp.departure_airport ==
                                     departure_airport_ident] if departure_airport_ident is not None else flightplans
            flightplan = random.choice(candidate_flightplane)
        callsign = callsign or self.generate_callsign()

        try:
            if flightplan.aircraft_icao == 'B738':
                aircraft = B738(
                    callsign=callsign,
                    flightplan=flightplan,
                    is_on_ground=True,
                    squawk_code='2000',
                    transponder_mode=TransponderMode.STANDBY
                )
            else:
                raise Exception('The aircraft is not supported')

            candidated_parkings: list[Parking] = []
            if parking is None:
                if len(airport.parkings) == 0:
                    raise Exception('No parking available at ' + airport.ident)
                candidated_parkings = airport.parkings
            else:
                candidated_parkings = [parking]

            occupied_parking_ids = [
                ac.parking.parking_id for ac in self.aircrafts.values()
                if (ac.parking is not None) and ac.status in (
                    AircraftStatus.NOT_DELIVERED,
                    AircraftStatus.DELIVERED,
                    AircraftStatus.APPROVED_PUSHBACK_STARTUP
                )
            ]
            empty_parkings = [
                p for p in candidated_parkings if p.parking_id not in occupied_parking_ids
            ]
            if len(empty_parkings) == 0:
                raise Exception('No parking available')
            parking = random.choice(empty_parkings)
            position = parking.position.copy()
            position.set_altitude(
                Distance(feet=airport.altitude)
            )
            aircraft.set_position(position)
            aircraft.set_parking(parking)

            self.aircrafts[callsign] = aircraft
            return aircraft

        except Exception as e:
            logger.exception(e)
            logger.debug(
                'Error occured on "%s %s %s"' % (
                    flightplan.departure_airport,
                    flightplan.route,
                    flightplan.arrival_airport
                )
            )
            return None

    def generate_on_approaching(
        self,
        arrival_airport_ident: str | None = None,
        callsign: str | None = None,
        flightplan: Flightplan | None = None,
        approach_id: int | None = None
    ):
        if flightplan is None:
            candidate_flightplane = flightplans
            if arrival_airport_ident is not None:
                candidate_flightplane = [
                    fp for fp in flightplans if fp.arrival_airport == arrival_airport_ident
                ]
            flightplan = random.choice(candidate_flightplane)
        callsign = callsign or self.generate_callsign()

        try:
            if flightplan.aircraft_icao == 'B738':
                aircraft = B738(
                    callsign=callsign,
                    flightplan=flightplan,
                    is_on_ground=False,
                    squawk_code='2000',
                    transponder_mode=TransponderMode.STANDBY
                )
            else:
                raise Exception('The aircraft is not supported')

            if approach_id is None:
                usable_approaches = flightplan.get_usable_approaches()
                usable_approaches = [
                    ap for ap in usable_approaches if ap.type in ('ILS', 'LOC')
                ]
                if len(usable_approaches) == 0:
                    raise Exception('No approach available')
                used_approach = random.choice(usable_approaches)
            else:
                used_approach = get_approach_by_id(approach_id)
                if used_approach is None:
                    raise Exception('No approach available')
            usable_transitions = used_approach.transitions
            used_transition = None
            if len(usable_transitions) != 0:
                used_transition = random.choice(usable_transitions)
            approach_legs = used_approach.approach_legs if used_approach is not None else []
            not_missed_approach_legs = [
                al for al in approach_legs if al.is_missed == 0]
            aircraft.set_approach_legs(
                fill_position_on_legs(
                    (used_transition.transition_legs if used_transition is not None else []) +
                    not_missed_approach_legs,
                    flightplan.arrival_airport
                )
            )
            aircraft.set_expect_runway_end(used_approach.runway_end)

            position = aircraft.legs[0].position.copy()
            position.set_altitude(Distance(feet=10000))
            aircraft.set_position(position)
            aircraft.set_speed(Speed(knots=200))
            aircraft.set_status(AircraftStatus.CLEARED_TAKEOFF)
            aircraft.set_transponder_mode_c()
            for leg in aircraft.legs:
                if leg.max_altitude_limit is not None:
                    aircraft.set_target_altitude(leg.max_altitude_limit)
                    break
            for leg in aircraft.legs:
                if leg.speed_limit is not None:
                    aircraft.set_speed_limit(leg.speed_limit)
                    break

            online_time = 380
            for _ in range(0, online_time, 2):
                if aircraft.is_no_more_legs:
                    return
                aircraft.update_status(timedelta(seconds=2))
                if aircraft.is_on_ground:
                    break

            self.aircrafts[callsign] = aircraft
            return aircraft

        except Exception as e:
            logger.exception(e)
            logger.debug(
                'Error occured on "%s %s %s"' % (
                    flightplan.arrival_airport,
                    flightplan.route,
                    flightplan.departure_airport
                )
            )
            return None
