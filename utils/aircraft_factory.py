import random

from aircrafts.b738 import B738
from utils.flightplan import Flightplan
from utils.physics import Speed
from helpers import fill_position_on_legs, get_start_leg

airline_icaos = ['CAL', 'EVA', 'SJX', 'CPA', 'FDX']
flightplans = [
    Flightplan(
        departure_airport='RCTP',
        arrival_airport='RCKH',
        flight_rules='I',
        cruise_speed=Speed(mph=489),
        route='CHALI T3 MKG W6 TNN',
        cruise_altitude=200,
    ),
    # TODO: support direct to waypoint in route
    # Flightplan(
    #     departure_airport='RCTP',
    #     arrival_airport='RCQC',
    #     flight_rules='I',
    #     cruise_speed=Speed(mph=489),
    #     route='CHALI T3 AJENT MASON',
    #     cruise_altitude=200,
    # ),
    Flightplan(
        departure_airport='VHHH',
        arrival_airport='RCTP',
        flight_rules='I',
        cruise_speed=Speed(mph=489),
        route='OCEAN V3 ENVAR M750 TONGA',
        cruise_altitude=370,
    ),
    Flightplan(
        departure_airport='RKSI',
        arrival_airport='RCTP',
        flight_rules='I',
        cruise_speed=Speed(mph=489),
        route='BOPTA Z51 BEDES Y711 MUGUS Y742 SALMI B576 BAKER',
        cruise_altitude=380,
    ),
    Flightplan(
        departure_airport='RCBS',
        arrival_airport='RCSS',
        flight_rules='I',
        cruise_speed=Speed(mph=489),
        route='INDIA W6 MKG A1 HLG',
        cruise_altitude=170,
    ),
    Flightplan(
        departure_airport='RCSS',
        arrival_airport='RCFN',
        flight_rules='I',
        cruise_speed=Speed(mph=489),
        route='YILAN B591 GI',
        cruise_altitude=180,
    ),
    Flightplan(
        departure_airport='RCTP',
        arrival_airport='RJBB',
        flight_rules='I',
        cruise_speed=Speed(mph=489),
        route='MOLKA M750 MOMPA Y451 HKC Y45 OOITA Y351 SALTY Y35 BERTH',
        cruise_altitude=390,
    ),
    Flightplan(
        departure_airport='RJBB',
        arrival_airport='RCTP',
        flight_rules='I',
        cruise_speed=Speed(mph=489),
        route='MAIKO Y34 SUKMO Y50 IGMON A1 DRAKE',
        cruise_altitude=380,
    ),
    Flightplan(
        departure_airport='RCTP',
        arrival_airport='ROAH',
        flight_rules='I',
        cruise_speed=Speed(mph=489),
        route='ROBIN R583 BORDO',
        cruise_altitude=330,
    ),
    Flightplan(
        departure_airport='ROAH',
        arrival_airport='RCTP',
        flight_rules='I',
        cruise_speed=Speed(mph=489),
        route='GANJU Y576 LILRA Y573 SEDKU R595 GRACE',
        cruise_altitude=320,
    ),
    Flightplan(
        departure_airport='RCTP',
        arrival_airport='ZSPD',
        flight_rules='I',
        cruise_speed=Speed(mph=489),
        route=' PIANO L3 VIOLA R596 SULEM DST B221 SHZ W58 BK',
        cruise_altitude=370,
    ),
]


class AircraftFactory:
    def __init__(self):
        self.aircrafts = {}

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
            aircraft = B738(
                callsign=callsign,
                flightplan=flightplan,
                is_on_ground=True
            )

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

            self.aircrafts[callsign] = aircraft
            return aircraft

        except Exception as e:
            print(flightplan)
            return None
