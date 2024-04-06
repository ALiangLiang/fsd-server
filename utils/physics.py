from datetime import timedelta

from geopy.distance import Distance


def get_acceleration_by_newton_2th(power_kg: float, aircraft_weight: float, drag_coefficient: float = 0.0):
    gravity = 9.81
    power_n = power_kg * gravity
    # N
    drag_force = 0.5 * drag_coefficient * aircraft_weight * gravity
    acceleration = (power_n - drag_force) / aircraft_weight
    return Acceleration(mps2=acceleration)


def cmp(a, b):
    return (a > b) - (a < b)


class Acceleration:
    def __init__(
        self,
        mps2: float | None = None,   # meters per second
    ):
        if mps2 is not None:
            self.__distance_per_sec2 = Distance(meters=mps2)
        else:
            raise ValueError(
                "Acceleration must be initialized with one of the units."
            )

    def __add__(self, other):
        if isinstance(other, Acceleration):
            return self.__class__(self.__distance_per_sec2.meters + other.__distance_per_sec2.meters)
        else:
            raise TypeError(
                "Acceleration instance must be added with Acceleration instance."
            )

    def __neg__(self):
        return self.__class__(-self.__distance_per_sec2.meters)

    def __sub__(self, other):
        return self + -other

    def __mul__(self, other):
        if isinstance(other, Acceleration):
            raise TypeError(
                "Acceleration instance must be multiplicated with numbers."
            )
        elif isinstance(other, timedelta):
            return Speed(mps=self.__distance_per_sec2.meters * other.total_seconds())
        else:
            return self.__class__(self.__distance_per_sec2.meters * other)

    def __rmul__(self, other):
        if isinstance(other, Acceleration):
            raise TypeError(
                "Acceleration instance must be multiplicated with numbers."
            )
        elif isinstance(other, timedelta):
            return Distance(meters=self.__distance_per_sec2 * other.total_seconds())
        else:
            return self.__class__(other * self.__distance_per_sec2.meters)

    def __truediv__(self, other):
        if isinstance(other, Acceleration):
            return self.__distance_per_sec2 / other.__distance_per_sec2
        else:
            return self.__class__(self.__distance_per_sec2.meters / other)

    def __floordiv__(self, other):
        if isinstance(other, Acceleration):
            return self.__distance_per_sec2 // other.__distance_per_sec2
        else:
            return self.__class__(self.__distance_per_sec2.meters // other)

    def __abs__(self):
        return self.__class__(abs(self.__distance_per_sec2.meters))

    def __bool__(self):
        return bool(self.__distance_per_sec2)

    def __repr__(self):  # pragma: no cover
        return 'Acceleration(%s)' % self.__distance_per_sec2

    def __str__(self):  # pragma: no cover
        return '%s m/s^2' % self.__distance_per_sec2.meters

    def __cmp__(self, other):  # py2 only
        if isinstance(other, Acceleration):
            return cmp(self.__distance_per_sec2, other.__distance_per_sec2)
        else:
            return cmp(self.__distance_per_sec2, other)

    def __hash__(self):
        return hash(self.__distance_per_sec2)

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

    @property
    def mps2(self) -> float:
        return self.__distance_per_sec2.meters


class Speed:
    def __init__(
        self,
        mps: float | None = None,   # meters per second
        mph: float | None = None,  # miles per hour
        kps: float | None = None,  # kilometers per second
        kph: float | None = None,  # kilometers per hour
        knots: float | None = None,  # nautical miles per hour
        fps: float | None = None,  # feet per second
        fpm: float | None = None,  # feet per minute
    ):
        if mps is not None:
            self.__distance_per_sec = Distance(meters=mps)
        elif mph is not None:
            self.__distance_per_sec = Distance(miles=mph / 3600)
        elif kps is not None:
            self.__distance_per_sec = Distance(kilometers=kps)
        elif kph is not None:
            self.__distance_per_sec = Distance(kilometers=kph / 3600)
        elif knots is not None:
            self.__distance_per_sec = Distance(nautical=knots / 3600)
        elif fps is not None:
            self.__distance_per_sec = Distance(feet=fps)
        elif fpm is not None:
            self.__distance_per_sec = Distance(feet=fpm / 60)
        else:
            raise ValueError(
                "Speed must be initialized with one of the units."
            )

    def __add__(self, other):
        if isinstance(other, Speed):
            return self.__class__(mps=self.__distance_per_sec.meters + other.__distance_per_sec.meters)
        else:
            raise TypeError(
                "Speed instance must be added with Speed instance."
            )

    def __neg__(self):
        return self.__class__(mps=-self.__distance_per_sec.meters)

    def __sub__(self, other):
        return self + -other

    def __mul__(self, other):
        if isinstance(other, Speed):
            raise TypeError(
                "Speed instance must be multiplicated with numbers."
            )
        elif isinstance(other, timedelta):
            return Distance(meters=self.__distance_per_sec.meters * other.total_seconds())
        else:
            return self.__class__(self.__distance_per_sec.meters * other)

    def __rmul__(self, other):
        if isinstance(other, Speed):
            raise TypeError(
                "Speed instance must be multiplicated with numbers."
            )
        elif isinstance(other, timedelta):
            return Distance(meters=self.__distance_per_sec * other.total_seconds())
        else:
            return self.__class__(other * self.__distance_per_sec.meters)

    def __truediv__(self, other):
        if isinstance(other, Speed):
            return self.__distance_per_sec / other.__distance_per_sec
        elif isinstance(other, Acceleration):
            return timedelta(seconds=self.__distance_per_sec.meters / other.mps2)
        else:
            return self.__class__(self.__distance_per_sec.meters / other)

    def __floordiv__(self, other):
        if isinstance(other, Speed):
            return self.__distance_per_sec // other.__distance_per_sec
        else:
            return self.__class__(self.__distance_per_sec.meters // other)

    def __abs__(self):
        return self.__class__(abs(self.__distance_per_sec.meters))

    def __bool__(self):
        return bool(self.__distance_per_sec)

    def __repr__(self):  # pragma: no cover
        return 'Speed(%s)' % self.__distance_per_sec

    def __str__(self):  # pragma: no cover
        return '%s m/s' % self.__distance_per_sec.meters

    def __cmp__(self, other):  # py2 only
        if isinstance(other, Speed):
            return cmp(self.__distance_per_sec, other.__distance_per_sec)
        else:
            return cmp(self.__distance_per_sec, other)

    def __hash__(self):
        return hash(self.__distance_per_sec)

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

    @property
    def mps(self) -> float:
        return self.__distance_per_sec.meters

    @property
    def mph(self) -> float:
        return self.__distance_per_sec.miles * 3600

    @property
    def kps(self) -> float:
        return self.__distance_per_sec.kilometers

    @property
    def kph(self) -> float:
        return self.__distance_per_sec.kilometers * 3600

    @property
    def knots(self) -> float:
        return self.__distance_per_sec.nautical * 3600

    @property
    def fps(self) -> float:
        return self.__distance_per_sec.feet

    @property
    def fpm(self) -> float:
        return self.__distance_per_sec.feet * 60
