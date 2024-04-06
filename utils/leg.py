from messages.Position import Position

from db.models import ApproachLeg, Airway, RunwayEnd, Waypoint, ProcedureLeg


class Leg:
    def __init__(
        self,
        ident: str,
        laty: float,
        lonx: float,
        altitude: float | None = None,
        is_missed: bool = False,
        waypoint: Waypoint | None = None
    ):
        self.ident = ident
        self.laty = laty
        self.lonx = lonx
        self.altitude = altitude
        self.is_missed = is_missed
        self.waypoint = waypoint

    @classmethod
    def from_procedure_leg(cls, procedure_leg: ProcedureLeg):
        return cls(
            ident=procedure_leg.fix_ident,
            laty=procedure_leg.fix_laty,
            lonx=procedure_leg.fix_lonx,
            is_missed=getattr(procedure_leg, 'is_missed', False),
        )

    @classmethod
    def from_airway(cls, airway: Airway):
        return cls(
            ident=airway.from_waypoint.ident,
            laty=airway.from_laty,
            lonx=airway.from_lonx,
            waypoint=airway.from_waypoint
        )

    @classmethod
    def from_airway_end(cls, airway: Airway):
        return cls(
            ident=airway.airway_name,
            laty=airway.to_laty,
            lonx=airway.to_lonx,
            waypoint=airway.to_waypoint
        )

    @classmethod
    def from_runway_end(cls, runway_end: RunwayEnd):
        return cls(
            ident='RW' + runway_end.name,
            laty=runway_end.laty,
            lonx=runway_end.lonx,
            altitude=runway_end.altitude
        )

    @property
    def position(self):
        return Position(self.laty, self.lonx, self.altitude)
