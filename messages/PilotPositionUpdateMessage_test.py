import unittest

from messages.PilotPositionUpdateMessage import PilotPositionUpdateMessage, TransponderMode
from messages.Position import Position
from utils.physics import Speed


class TestPilotPositionUpdateMessage(unittest.TestCase):
    def test_init(self):
        PilotPositionUpdateMessage(
            'CAL123',
            TransponderMode.MODE_C,
            '2000',
            '4',
            Position(0, 0),
            0,
            Speed(0),
            (0, 0, 0, False),
            0
        )

    def test_tuple_to_pbh(self):
        msg = PilotPositionUpdateMessage(
            'CAL123',
            TransponderMode.MODE_C,
            '2000',
            '4',
            Position(0, 0),
            0,
            Speed(0),
            (0.703125, 0.0, 337.1484375, True),
            0
        )
        msg.tuple_to_pbh()

    def test_pbh_to_tuple(self):
        PilotPositionUpdateMessage.pbh_to_tuple(4261414408)
