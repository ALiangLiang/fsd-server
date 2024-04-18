from geopy.point import Point
from geopy.distance import Distance


class Position(Point):
    def __init__(self, latitude: float, longitude: float, altitude: Distance | None = None):
        super().__new__(Position, latitude=latitude, longitude=longitude)
        self.altitude = 0.0
        self.altitude_ = altitude

    def __new__(cls, latitude: float, longitude: float, altitude: Distance | None = None):
        return super().__new__(cls, latitude, longitude)

    @staticmethod
    def from_point(point: Point):
        return Position(point.latitude, point.longitude, Distance(feet=point.altitude))

    @staticmethod
    def parse_raw_message(raw_message):
        args = raw_message.split(':')
        lat = args[0]
        lng = args[1]
        return Position(lat, lng)

    def copy(self):
        return Position(self.latitude, self.longitude, self.altitude_)

    def set_coordinates(self, latitude: float, longitude: float):
        self.latitude = latitude
        self.longitude = longitude

    def add_altitude(self, altitude: Distance):
        self.altitude_ += altitude
        return self

    def set_altitude(self, altitude: Distance):
        self.altitude_ = altitude
        return self

    def __str__(self):
        return f"{self.latitude}:{self.longitude}"

    def __hash__(self):
        return hash((self.latitude, self.longitude, self.altitude_))
