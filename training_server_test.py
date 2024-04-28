import unittest
from geopy.distance import distance

import astar

from training_server import get_vatated_taxi_path_by_runway
from helpers import get_airport_by_ident


class TestHelpers(unittest.TestCase):

    def test_get_vatated_taxi_path_by_runway(self):
        airport = get_airport_by_ident('RCTP')
        get_vatated_taxi_path_by_runway(airport.airport_id, '05L')
