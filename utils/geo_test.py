import unittest

from messages.Position import Position
from utils.geo import get_mag_var_by_position


class TestGeo(unittest.TestCase):

    def test_get_mag_var_by_position(self):
        print(get_mag_var_by_position(Position(
            latitude=25.079457142147316,
            longitude=121.23277778392557
        )))
        print(get_mag_var_by_position(Position(
            latitude=22.57776183044977,
            longitude=120.34622858903228
        )))