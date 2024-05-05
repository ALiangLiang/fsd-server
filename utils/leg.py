from geopy.distance import Distance

from messages.Position import Position
from utils.physics import Speed
from utils.bearing import Bearing
from db.models import Fix, Airway, RunwayEnd, ProcedureLeg, ApproachFixType, ProcedureLegType


class Leg:
    def __init__(
        self,
        ident: str,
        laty: float,
        lonx: float,
        altitude: Distance | None = None,
        is_missed: bool = False,
        fix: Fix | None = None,
        max_altitude_limit: Distance | None = None,
        min_altitude_limit: Distance | None = None,
        speed_limit: Speed | None = None,
        course: Bearing | None = None,
        glide_slope_angle: float | None = None,
        is_holding_fix: bool = False,
        procedure_leg_type: ProcedureLegType | None = None,
        procedure_leg: ProcedureLeg | None = None
    ):
        self.ident = ident
        self.laty = laty
        self.lonx = lonx
        self.altitude = altitude
        self.is_missed = is_missed
        self.fix = fix
        self.max_altitude_limit = max_altitude_limit
        self.min_altitude_limit = min_altitude_limit
        self.speed_limit = speed_limit
        self.course = course
        self.glide_slope_angle = glide_slope_angle
        self.is_holding_fix = is_holding_fix
        self.procedure_leg_type = procedure_leg_type
        self.procedure_leg = procedure_leg

    @classmethod
    def from_procedure_leg(cls, procedure_leg: ProcedureLeg, fix: Fix | None = None):
        is_missed_flag = getattr(procedure_leg, 'is_missed', 0)
        procedure_leg_type = ProcedureLegType(procedure_leg.type)

        altitude_1 = Distance(
            feet=procedure_leg.altitude1
        ) if procedure_leg.altitude1 is not None else None
        altitude_2 = Distance(
            feet=procedure_leg.altitude2
        ) if procedure_leg.altitude2 is not None else None

        match procedure_leg_type:
            case ProcedureLegType.HEADING_TO_ALTITUDE_TERMINATION | ProcedureLegType.HOLD_TO_MANUAL_TERMINATION:
                max_altitude_limit = None
                min_altitude_limit = altitude_1
            case ProcedureLegType.HEADING_TO_DME_DISTANCE_TERMINATION:
                max_altitude_limit = None
                min_altitude_limit = None
            case ProcedureLegType.DIRECT_TO_FIX:
                max_altitude_limit = altitude_1
                min_altitude_limit = altitude_1
            case _:
                max_altitude_limit = altitude_1
                min_altitude_limit = altitude_2

        return cls(
            ident=procedure_leg.fix_ident,
            laty=procedure_leg.fix_laty,
            lonx=procedure_leg.fix_lonx,
            fix=fix,
            is_missed=bool(is_missed_flag),
            max_altitude_limit=max_altitude_limit,
            min_altitude_limit=min_altitude_limit,
            speed_limit=Speed(
                knots=procedure_leg.speed_limit
            ) if procedure_leg.speed_limit is not None else None,
            course=Bearing(
                procedure_leg.course
            ) if procedure_leg.course is not None else None,
            glide_slope_angle=procedure_leg.vertical_angle,
            is_holding_fix=procedure_leg.approach_fix_type == ApproachFixType.HOLDING_FIX.value,
            procedure_leg_type=procedure_leg_type,
            procedure_leg=procedure_leg
        )

    @classmethod
    def from_airway(cls, airway: Airway):
        return cls(
            ident=airway.from_waypoint.ident,
            laty=airway.from_laty,
            lonx=airway.from_lonx,
            fix=airway.from_waypoint
        )

    @classmethod
    def from_airway_end(cls, airway: Airway):
        return cls(
            ident=airway.to_waypoint.ident,
            laty=airway.to_laty,
            lonx=airway.to_lonx,
            fix=airway.to_waypoint
        )

    @classmethod
    def from_runway_end(cls, runway_end: RunwayEnd):
        return cls(
            ident='RW' + runway_end.name,
            laty=runway_end.laty,
            lonx=runway_end.lonx,
            altitude=Distance(feet=runway_end.altitude)
        )

    @property
    def position(self):
        return Position(
            self.laty,
            self.lonx,
            self.altitude
        )
