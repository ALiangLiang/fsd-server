from geopy.point import Point


class Position(Point):
    def __init__(self, latitude: float, longitude: float):
        super().__new__(Position, latitude=latitude, longitude=longitude)

    @staticmethod
    def from_point(point: Point):
        return Position(point.latitude, point.longitude)

    @staticmethod
    def parse_raw_message(raw_message):
        args = raw_message.split(':')
        lat = args[0]
        lng = args[1]
        return Position(lat, lng)

    def __str__(self):
        return f"{self.latitude}:{self.longitude}"
