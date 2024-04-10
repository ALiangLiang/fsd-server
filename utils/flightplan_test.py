import unittest

from utils.distance import Distance

from utils.physics import Speed
from utils.flightplan import Flightplan


class TestFlightplan(unittest.TestCase):

    def test_get_usable_sids(self):
        flightplan = Flightplan(
            departure_airport='RCTP',
            arrival_airport='RCKH',
            flight_rules='I',
            cruise_speed=Speed(mph=489),
            route='CHALI T3 MKG W6 TNN',
            cruise_altitude=Distance(feet=200),
        )

        self.assertEqual(len(flightplan.get_usable_sids()), 4)

        flightplan = Flightplan(
            departure_airport='RCSS',
            arrival_airport='RCFN',
            flight_rules='I',
            cruise_speed=Speed(mph=489),
            route='YILAN B591 GI',
            cruise_altitude=Distance(feet=200),
        )
        self.assertEqual(len(flightplan.get_usable_sids()), 4)

    def test_get_usable_stars(self):
        flightplan = Flightplan(
            departure_airport='RCTP',
            arrival_airport='RCKH',
            flight_rules='I',
            cruise_speed=Speed(mph=489),
            route='CHALI T3 MKG W6 TNN',
            cruise_altitude=Distance(feet=200),
        )
        self.assertEqual(len(flightplan.get_usable_stars()), 2)

    def test_get_usable_approaches(self):
        flightplan = Flightplan(
            departure_airport='RCTP',
            arrival_airport='RCKH',
            flight_rules='I',
            cruise_speed=Speed(mph=489),
            route='CHALI T3 MKG W6 TNN',
            cruise_altitude=Distance(feet=200),
        )
        usable_stars = flightplan.get_usable_stars()
        used_star = usable_stars[0]
        usable_approaches = flightplan.get_usable_approaches(used_star)
