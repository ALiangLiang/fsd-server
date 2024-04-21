from random import choice
from typing import Any

from geopy.distance import Distance

from utils.flightplan import Flightplan
from utils.physics import Speed

b738_config: dict[str, Any] = dict(
    aircraft_icao='B738',
    equipment='SDE2E3FGHIRWXY',
    transponder_types='LB1',
    wake_turbulence_category='M',
    cruise_speed=Speed(mph=489),
)

flightplans = [
    # Taiwan
    Flightplan(
        departure_airport='RCTP',
        arrival_airport='RCKH',
        flight_rules='I',
        route='CHALI T3 MKG W6 TNN',
        cruise_altitude=choice((
            Distance(feet=20000),
            Distance(feet=18000),
        )),
        **b738_config
    ),
    Flightplan(
        departure_airport='RCKH',
        arrival_airport='RCTP',
        flight_rules='I',
        route='TNN',
        cruise_altitude=choice((
            Distance(feet=19000),
            Distance(feet=17000),
        )),
        **b738_config
    ),
    Flightplan(
        departure_airport='RCYU',
        arrival_airport='RCMQ',
        flight_rules='I',
        route='TINHO B591 WADER J4 HLG W4 GUBAO',
        cruise_altitude=Distance(feet=18000),
        **b738_config
    ),
    # Flightplan(
    #     departure_airport='RCMQ',
    #     arrival_airport='RCQC',
    #     flight_rules='I',
    #     route='WUCHI A1 SWORD',
    #     cruise_altitude=Distance(feet=8000),
    #     **b738_config
    # ),
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
        departure_airport='RCFN',
        arrival_airport='RCSS',
        flight_rules='I',
        route='DONNA B591 YILAN',
        cruise_altitude=Distance(feet=17000),
        **b738_config
    ),
    Flightplan(
        departure_airport='RCBS',
        arrival_airport='RCSS',
        flight_rules='I',
        route='INDIA W6 MKG A1 HLG',
        cruise_altitude=Distance(feet=17000),
        **b738_config
    ),
    Flightplan(
        departure_airport='RCSS',
        arrival_airport='RCFN',
        flight_rules='I',
        route='YILAN B591 GI',
        cruise_altitude=Distance(feet=18000),
        **b738_config
    ),
    Flightplan(
        departure_airport='RCFN',
        arrival_airport='RCSS',
        flight_rules='I',
        route='DONNA B591 YILAN',
        cruise_altitude=Distance(feet=17000),
        **b738_config
    ),

    # Korea
    Flightplan(
        departure_airport='RCTP',
        arrival_airport='RKSI',
        flight_rules='I',
        route='PIANO L3 SALMI Y743 BOLUT Y741 ATOTI Y722 OLMEN',
        cruise_altitude=choice((
            Distance(feet=35000),
            Distance(feet=37000),
            Distance(feet=39000),
            Distance(feet=41000),
        )),
        **b738_config
    ),
    Flightplan(
        departure_airport='RKSI',
        arrival_airport='RCTP',
        flight_rules='I',
        route='BOPTA Z51 BEDES Y711 MUGUS Y742 SALMI B576 BAKER',
        cruise_altitude=choice((
            Distance(feet=34000),
            Distance(feet=36000),
            Distance(feet=38000),
            Distance(feet=40000),
        )),
        **b738_config
    ),
    Flightplan(
        departure_airport='RCTP',
        arrival_airport='RKSS',
        flight_rules='I',
        route='PIANO L3 SALMI Y743 BOLUT Y741 ATOTI Y722 OLMEN',
        cruise_altitude=choice((
            Distance(feet=35000),
            Distance(feet=37000),
            Distance(feet=39000),
            Distance(feet=41000),
        )),
        **b738_config
    ),
    Flightplan(
        departure_airport='RKSS',
        arrival_airport='RCTP',
        flight_rules='I',
        route='BULTI Y711 MUGUS Y742 SALMI B576 BAKER',
        cruise_altitude=choice((
            Distance(feet=34000),
            Distance(feet=36000),
            Distance(feet=38000),
            Distance(feet=40000),
        )),
        **b738_config
    ),
    Flightplan(
        departure_airport='RCTP',
        arrival_airport='RKPC',
        flight_rules='I',
        route='PIANO L3 SALMI B576 SOSDO',
        cruise_altitude=choice((
            Distance(feet=35000),
            Distance(feet=37000),
            Distance(feet=39000),
            Distance(feet=41000),
        )),
        **b738_config
    ),
    Flightplan(
        departure_airport='RKPC',
        arrival_airport='RCTP',
        flight_rules='I',
        route='PANSI Y711 MUGUS Y742 SALMI B576 BAKER',
        cruise_altitude=choice((
            Distance(feet=34000),
            Distance(feet=36000),
            Distance(feet=38000),
            Distance(feet=40000),
        )),
        **b738_config
    ),

    # Japan
    Flightplan(
        departure_airport='RCTP',
        arrival_airport='RJAA',
        flight_rules='I',
        route='MOLKA M750 ANKIX Y891 AGIMO Y89 GUPER Y81 RUTAS',
        cruise_altitude=choice((
            Distance(feet=35000),
            Distance(feet=37000),
            Distance(feet=39000),
            Distance(feet=41000),
        )),
        **b738_config
    ),
    Flightplan(
        departure_airport='RJAA',
        arrival_airport='RCTP',
        flight_rules='I',
        route='PIGOK Y50 IGMON A1 DRAKE',
        cruise_altitude=choice((
            Distance(feet=34000),
            Distance(feet=36000),
            Distance(feet=38000),
            Distance(feet=40000),
        )),
        **b738_config
    ),
    Flightplan(
        departure_airport='RCTP',
        arrival_airport='RJBB',
        flight_rules='I',
        route='MOLKA M750 MADOG Y53 BECKY',
        cruise_altitude=choice((
            Distance(feet=35000),
            Distance(feet=37000),
            Distance(feet=39000),
            Distance(feet=41000),
        )),
        **b738_config
    ),
    Flightplan(
        departure_airport='RJBB',
        arrival_airport='RCTP',
        flight_rules='I',
        route='MAIKO Y34 SUKMO Y50 IGMON A1 DRAKE',
        cruise_altitude=choice((
            Distance(feet=34000),
            Distance(feet=36000),
            Distance(feet=38000),
            Distance(feet=40000),
        )),
        **b738_config
    ),
    Flightplan(
        departure_airport='RCTP',
        arrival_airport='RJTT',
        flight_rules='I',
        route='MOLKA M750 BILLY Y21 AKSEL',
        cruise_altitude=choice((
            Distance(feet=35000),
            Distance(feet=37000),
            Distance(feet=39000),
            Distance(feet=41000),
        )),
        **b738_config
    ),
    Flightplan(
        departure_airport='RJTT',
        arrival_airport='RCTP',
        flight_rules='I',
        route='LAXAS Y56 TOHME Y54 TURFY Y24 KOSHI Y50 IGMON A1 DRAKE',
        cruise_altitude=choice((
            Distance(feet=34000),
            Distance(feet=36000),
            Distance(feet=38000),
            Distance(feet=40000),
        )),
        **b738_config
    ),
    Flightplan(
        departure_airport='RCTP',
        arrival_airport='ROAH',
        flight_rules='I',
        route='KUDOS R595 SEDKU Y573 MJC Y57 VELNO',
        cruise_altitude=choice((
            Distance(feet=35000),
            Distance(feet=37000),
            Distance(feet=39000),
            Distance(feet=41000),
        )),
        **b738_config
    ),
    Flightplan(
        departure_airport='ROAH',
        arrival_airport='RCTP',
        flight_rules='I',
        route='GANJU Y576 LILRA Y573 SEDKU R595 GRACE',
        cruise_altitude=choice((
            Distance(feet=34000),
            Distance(feet=36000),
            Distance(feet=38000),
            Distance(feet=40000),
        )),
        **b738_config
    ),

    # China
    Flightplan(
        departure_airport='RCTP',
        arrival_airport='ZSPD',
        flight_rules='I',
        route='PIANO L3 VIOLA R596 SULEM R596 DST B221 PAMVU V74 BK',
        cruise_altitude=choice((
            Distance(feet=25000),
            Distance(feet=29000),
            Distance(feet=37000),
        )),
        **b738_config
    ),
    Flightplan(
        departure_airport='ZSPD',
        arrival_airport='RCTP',
        flight_rules='I',
        route='MIGOL B591 KASKA B591 BAKER',
        cruise_altitude=choice((
            Distance(feet=24000),
            Distance(feet=28000),
            Distance(feet=34000),
        )),
        **b738_config
    ),
    Flightplan(
        departure_airport='RCTP',
        arrival_airport='ZSAM',
        flight_rules='I',
        route='CHALI T3 MKG A1 ANPOG R200 LAPUG R200 BEBEM A470 TEBON',
        cruise_altitude=Distance(feet=28000),
        **b738_config
    ),
    Flightplan(
        departure_airport='ZSAM',
        arrival_airport='RCTP',
        flight_rules='I',
        route='NUSPA W597 IKATA A470 BEBEM R200 EXTRA M750 TONGA',
        cruise_altitude=Distance(feet=29000),
        **b738_config
    ),
    Flightplan(
        departure_airport='RCTP',
        arrival_airport='VHHH',
        flight_rules='I',
        route='CHALI T3 MKG A1 ELATO V522 ABBEY',
        cruise_altitude=choice((
            Distance(feet=34000),
            Distance(feet=36000),
            Distance(feet=38000),
            Distance(feet=40000),
        )),
        **b738_config
    ),
    Flightplan(
        departure_airport='VHHH',
        arrival_airport='RCTP',
        flight_rules='I',
        route='OCEAN V3 ENVAR M750 TONGA',
        cruise_altitude=choice((
            Distance(feet=35000),
            Distance(feet=37000),
            Distance(feet=39000),
            Distance(feet=41000),
        )),
        **b738_config
    ),

    # Philippines
    Flightplan(
        departure_airport='RCTP',
        arrival_airport='RPLL',
        flight_rules='I',
        route='TINHO B591 GID Q11 POTIB M646 LAO B462 CAB',
        cruise_altitude=choice((
            Distance(feet=30000),
            Distance(feet=34000),
            Distance(feet=38000),
        )),
        **b738_config
    ),
    Flightplan(
        departure_airport='RPLL',
        arrival_airport='RCTP',
        flight_rules='I',
        route='CAB B462 LAO M646 POTIB Q14 TNN',
        cruise_altitude=choice((
            Distance(feet=33000),
            Distance(feet=35000),
            Distance(feet=37000),
            Distance(feet=39000),
        )),
        **b738_config
    ),
]
