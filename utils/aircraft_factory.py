import random
import logging
from datetime import timedelta

from geopy.distance import Distance

from aircrafts.b738 import B738
from utils.flightplan import Flightplan
from utils.physics import Speed
from utils.squawk_code import generate_taipei_fir_squawk_code
from helpers import fill_position_on_legs, get_start_leg
from aircrafts.aircraft import Aircraft

logger = logging.getLogger(__name__)

airline_icaos = ['CAL', 'EVA', 'SJX', 'CPA', 'FDX']
flightplans = [
    Flightplan(
        departure_airport='RCTP',
        arrival_airport='RCKH',
        flight_rules='I',
        cruise_speed=Speed(mph=489),
        route='CHALI T3 MKG W6 TNN',
        cruise_altitude=Distance(feet=20000),
        aircraft_icao='B738',
        equipment='SDE2E3FGHIRWXY',
        transponder_types='LB1',
    ),
    # TODO: support direct to waypoint in route
    # Flightplan(
    #     departure_airport='RCTP',
    #     arrival_airport='RCQC',
    #     flight_rules='I',
    #     cruise_speed=Speed(mph=489),
    #     route='CHALI T3 AJENT MASON',
    #     cruise_altitude=Distance(feet=200,
    # ),
    Flightplan(
        departure_airport='VHHH',
        arrival_airport='RCTP',
        flight_rules='I',
        cruise_speed=Speed(mph=489),
        route='OCEAN V3 ENVAR M750 TONGA',
        cruise_altitude=Distance(feet=37000),
        aircraft_icao='B738',
        wake_turbulence_category='M',
        equipment='SDE2E3FGHIRWXY',
        transponder_types='LB1',
    ),
    Flightplan(
        departure_airport='RKSI',
        arrival_airport='RCTP',
        flight_rules='I',
        cruise_speed=Speed(mph=489),
        route='BOPTA Z51 BEDES Y711 MUGUS Y742 SALMI B576 BAKER',
        cruise_altitude=Distance(feet=38000),
        aircraft_icao='B738',
        wake_turbulence_category='M',
        equipment='SDE2E3FGHIRWXY',
        transponder_types='LB1',
    ),
    Flightplan(
        departure_airport='RCBS',
        arrival_airport='RCSS',
        flight_rules='I',
        cruise_speed=Speed(mph=489),
        route='INDIA W6 MKG A1 HLG',
        cruise_altitude=Distance(feet=17000),
        aircraft_icao='B738',
        wake_turbulence_category='M',
        equipment='SDE2E3FGHIRWXY',
        transponder_types='LB1',
    ),
    Flightplan(
        departure_airport='RCSS',
        arrival_airport='RCFN',
        flight_rules='I',
        cruise_speed=Speed(mph=489),
        route='YILAN B591 GI',
        cruise_altitude=Distance(feet=18000),
        aircraft_icao='B738',
        wake_turbulence_category='M',
        equipment='SDE2E3FGHIRWXY',
        transponder_types='LB1',
    ),
    Flightplan(
        departure_airport='RCTP',
        arrival_airport='RJBB',
        flight_rules='I',
        cruise_speed=Speed(mph=489),
        route='MOLKA M750 MOMPA Y451 HKC Y45 OOITA Y351 SALTY Y35 BERTH',
        cruise_altitude=Distance(feet=39000),
        aircraft_icao='B738',
        wake_turbulence_category='M',
        equipment='SDE2E3FGHIRWXY',
        transponder_types='LB1',
    ),
    Flightplan(
        departure_airport='RJBB',
        arrival_airport='RCTP',
        flight_rules='I',
        cruise_speed=Speed(mph=489),
        route='MAIKO Y34 SUKMO Y50 IGMON A1 DRAKE',
        cruise_altitude=Distance(feet=38000),
        aircraft_icao='B738',
        wake_turbulence_category='M',
        equipment='SDE2E3FGHIRWXY',
        transponder_types='LB1',
    ),
    Flightplan(
        departure_airport='RCTP',
        arrival_airport='ROAH',
        flight_rules='I',
        cruise_speed=Speed(mph=489),
        route='ROBIN R583 BORDO',
        cruise_altitude=Distance(feet=33000),
        aircraft_icao='B738',
        wake_turbulence_category='M',
        equipment='SDE2E3FGHIRWXY',
        transponder_types='LB1',
    ),
    Flightplan(
        departure_airport='ROAH',
        arrival_airport='RCTP',
        flight_rules='I',
        cruise_speed=Speed(mph=489),
        route='GANJU Y576 LILRA Y573 SEDKU R595 GRACE',
        cruise_altitude=Distance(feet=32000),
        aircraft_icao='B738',
        wake_turbulence_category='M',
        equipment='SDE2E3FGHIRWXY',
        transponder_types='LB1',
    ),
    Flightplan(
        departure_airport='RCYU',
        arrival_airport='RCMQ',
        flight_rules='I',
        cruise_speed=Speed(mph=489),
        route='TINHO B591 WADER J4 HLG W4 GUBAO',
        cruise_altitude=Distance(feet=18000),
        aircraft_icao='B738',
        wake_turbulence_category='M',
        equipment='SDE2E3FGHIRWXY',
        transponder_types='LB1',
    ),
    Flightplan(
        departure_airport='RCTP',
        arrival_airport='RKSS',
        flight_rules='I',
        cruise_speed=Speed(mph=489),
        route='PIANO L3 SALMI Y743 BOLUT Y741 ATOTI Y722 OLMEN',
        cruise_altitude=Distance(feet=35000),
        aircraft_icao='B738',
        wake_turbulence_category='M',
        equipment='SDE2E3FGHIRWXY',
        transponder_types='LB1',
    ),
    # Flightplan(
    #     departure_airport='RCMQ',
    #     arrival_airport='RCQC',
    #     flight_rules='I',
    #     cruise_speed=Speed(mph=489),
    #     route='WUCHI A1 SWORD',
    #     cruise_altitude=Distance(feet=8000),
    #     aircraft_icao='B738',
    #     wake_turbulence_category='M',
    #     equipment='SDE2E3FGHIRWXY',
    #     transponder_types='LB1',
    # ),
    Flightplan(
        departure_airport='RCFN',
        arrival_airport='RCSS',
        flight_rules='I',
        cruise_speed=Speed(mph=489),
        route='DONNA B591 YILAN',
        cruise_altitude=Distance(feet=17000),
        aircraft_icao='B738',
        wake_turbulence_category='M',
        equipment='SDE2E3FGHIRWXY',
        transponder_types='LB1',
    ),
    # Flightplan(
    #     departure_airport='RCTP',
    #     arrival_airport='ZSPD',
    #     flight_rules='I',
    #     cruise_speed=Speed(mph=489),
    #     route='PIANO L3 VIOLA R596 SULEM DST B221 SHZ W58 BK',
    #     cruise_altitude=Distance(feet=37000),
    #     aircraft_icao='B738',
    # ),
]


class AircraftFactory:
    aircrafts: dict[str, Aircraft] = {}

    def generate_callsign(self):
        def generate_random_callsign():
            return f'{random.choice(airline_icaos)}{random.randint(100, 999)}'
        callsign = generate_random_callsign()
        while self.aircrafts.get(callsign) is not None:
            callsign = generate_random_callsign()
        return callsign

    def generate_flightplan(self):
        return f'{random.choice(airline_icaos)}{random.randint(100, 999)}'

    def generate_w_random_situation(self):
        is_in_air = random.choice([True, False])
        # if is_in_air:
        #     aircraft = B738(
        #         callsign=self.generate_callsign(),
        #         position=Position()
        #         is_on_ground=False
        #     )
        # else:
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

            online_time = random.randint(0, 3600 / 2) * 2
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
