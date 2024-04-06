from datetime import timedelta
import unittest

from geopy.distance import Distance

from utils.physics import Speed, Acceleration


class TestAcceleration(unittest.TestCase):

    def test_init_acceleration(self):
        acceleration = Acceleration(mps2=10)
        self.assertEqual(acceleration.mps2, 10)


class TestSpeed(unittest.TestCase):

    def test_init_speed(self):
        speed = Speed(mps=10)
        self.assertEqual(speed.mps, 10)

        speed = Speed(mph=10)
        self.assertAlmostEqual(speed.mps, 4.4704)

        speed = Speed(kps=10)
        self.assertEqual(speed.mps, 10000)

        speed = Speed(kph=10)
        self.assertEqual(speed.mps, 2.7777777777777777)

        speed = Speed(knots=10)
        self.assertAlmostEqual(speed.mps, 5.144444444444444)

    def test_unit_conversion(self):
        speed = Speed(mps=10)
        self.assertAlmostEqual(speed.mph, 22.369362920544)

        speed = Speed(mph=10)
        self.assertAlmostEqual(speed.kps, 0.0044704)

        speed = Speed(kps=10)
        self.assertEqual(speed.kph, 36000)

        speed = Speed(kph=10)
        self.assertAlmostEqual(speed.knots, 5.399568034557235)

        speed = Speed(knots=10)
        self.assertAlmostEqual(speed.mps, 5.144444444444444)

    def test_add_speed_w_same_unit(self):
        speed1 = Speed(mps=10)
        speed2 = Speed(mps=20)
        speed = speed1 + speed2
        self.assertEqual(speed.mps, 30)

    def test_add_speed_w_diff_unit(self):
        speed1 = Speed(mps=10)
        speed2 = Speed(mph=20)
        speed = speed1 + speed2
        self.assertAlmostEqual(speed.mps, 18.9408)

    def test_sub_speed_w_same_unit(self):
        speed1 = Speed(mps=20)
        speed2 = Speed(mps=10)
        speed = speed1 - speed2
        self.assertEqual(speed.mps, 10)

    def test_sub_speed_w_diff_unit(self):
        speed1 = Speed(mps=20)
        speed2 = Speed(mph=10)
        speed = speed1 - speed2
        self.assertAlmostEqual(speed.mps, 15.5296)

    def test_mul_speed_w_number(self):
        speed = Speed(mps=10)
        speed = speed * 2
        self.assertEqual(speed.mps, 20)

    def test_mul_speed_w_timedelta(self):
        speed = Speed(mps=10)
        speed = speed * timedelta(seconds=2)
        self.assertEqual(speed, Distance(meters=20))

    def test_div_by_acceleration(self):
        speed = Speed(mps=10)
        acceleration = Acceleration(mps2=2)
        self.assertEqual(speed / acceleration, timedelta(seconds=5))


if __name__ == '__main__':
    unittest.main()
