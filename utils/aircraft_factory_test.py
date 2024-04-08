import unittest

from utils.physics import Speed
from utils.aircraft_factory import AircraftFactory


class TestAircraftFactory(unittest.TestCase):

    def test_generate_callsign(self):
        factory = AircraftFactory()
        callsign = factory.generate_callsign()
        self.assertEqual(len(callsign), 6)

    def test_generate_w_random_situation(self):
        factory = AircraftFactory()
        aircraft = factory.generate_w_random_situation()
        print([l.ident for l in aircraft.legs])
