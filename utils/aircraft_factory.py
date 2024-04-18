import random
import logging
from datetime import timedelta

from geopy.distance import Distance

from aircrafts.b738 import B738
from utils.squawk_code import generate_taipei_fir_squawk_code
from utils.flight_plans import flightplans
from helpers import fill_position_on_legs, get_start_leg, get_airport_by_ident
from aircrafts.bot_aircraft import BotAircraft, TransponderMode

logger = logging.getLogger(__name__)

airline_icaos = ['CAL', 'EVA', 'SJX', 'CPA', 'FDX']


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

    def generate_on_parking(self, departure_airport_ident: str | None):
        candidate_flightplane = [fp for fp in flightplans if fp.departure_airport ==
                                 departure_airport_ident] if departure_airport_ident is not None else flightplans
        flightplan = random.choice(candidate_flightplane)
        callsign = self.generate_callsign()

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
                return

            airport = get_airport_by_ident(flightplan.departure_airport)
            if airport is None:
                return
            if len(airport.parkings) == 0:
                logger.error('No parking available at %s' % airport.ident)
                return

            parking = random.choice(airport.parkings)
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
