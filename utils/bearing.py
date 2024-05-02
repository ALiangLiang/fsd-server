def cmp(a, b):
    return (a > b) - (a < b)


class Bearing:
    def __init__(self, heading: float, mag_var: float = 0.0):
        self.heading = heading % 360
        self.mag_var = mag_var

    @property
    def degrees(self):
        return self.heading - self.mag_var

    def __str__(self):
        return f'{self.degrees:.1f}°'

    def __cmp__(self, other):  # py2 only
        return cmp(self.degrees, other.degrees)

    def __add__(self, other):
        # maintain the range of 0-360
        return Bearing((self.degrees + other.degrees) % 360)

    def __sub__(self, other):
        return Bearing((self.degrees - other.degrees) % 360)

    def __mul__(self, other):
        return Bearing(self.degrees * other % 360)

    def __eq__(self, other):
        return self.__cmp__(other) == 0

    def __ne__(self, other):
        return self.__cmp__(other) != 0

    def __gt__(self, other):
        return self.__cmp__(other) > 0

    def __lt__(self, other):
        return self.__cmp__(other) < 0

    def __ge__(self, other):
        return self.__cmp__(other) >= 0

    def __le__(self, other):
        return self.__cmp__(other) <= 0
