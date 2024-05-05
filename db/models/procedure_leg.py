from enum import Enum

from sqlalchemy import Column, Integer, String, Float

from messages.Position import Position


class ApproachFixType(Enum):
    IAF = 'A'
    MAP = 'M'
    HOLDING_FIX = 'H'


class ProcedureLegType(Enum):
    ARC_TO_FIX = 'AF'
    COURSE_TO_ALTITUDE = 'CA'
    COURSE_TO_DME_DISTANCE = 'CD'
    COURSE_TO_FIX = 'CF'
    COURSE_TO_INTERCEPT = 'CI'
    COURSE_TO_RADIAL_TERMINATION = 'CR'
    DIRECT_TO_FIX = 'DF'
    FIX_TO_ALTITUDE = 'FA'
    TRACK_FROM_FIX_FROM_DISTANCE = 'FC'
    TRACK_FROM_FIX_TO_DME_DISTANCE = 'FD'
    FROM_FIX_TO_MANUAL_TERMINATION = 'FM'
    HOLD_TO_ALTITUDE = 'HA'
    HOLD_TO_FIX = 'HF'
    HOLD_TO_MANUAL_TERMINATION = 'HM'
    INITIAL_FIX = 'IF'
    PROCEDURE_TURN = 'PI'
    CONSTANT_RADIUS_ARC = 'RF'
    TRACK_TO_FIX = 'TF'
    HEADING_TO_ALTITUDE_TERMINATION = 'VA'
    HEADING_TO_DME_DISTANCE_TERMINATION = 'VD'
    HEADING_TO_INTERCEPT = 'VI'
    HEADING_TO_MANUAL_TERMINATION = 'VM'
    HEADING_TO_RADIAL_TERMINATION = 'VR'
    DIRECT_TO_RUNWAY = 'RX'
    CIRCLE_TO_LAND = 'CX'
    STRAIGHT_IN = 'TX'
    START_OF_PROCEDURE = 'SX'
    VECTORS = 'VX'
    CUSTOM_APP_START = 'CFX'
    CUSTOM_APP_RUNWAY = 'CRX'
    CUSTOM_DEP_END = 'CDX'
    CUSTOM_DEP_RUNWAY = 'CDR'


class ProcedureLeg:
    # AF = ARC_TO_FIX
    # CA = COURSE_TO_ALTITUDE
    # CD = COURSE_TO_DME_DISTANCE
    # CF = COURSE_TO_FIX
    # CI = COURSE_TO_INTERCEPT
    # CR = COURSE_TO_RADIAL_TERMINATION
    # DF = DIRECT_TO_FIX
    # FA = FIX_TO_ALTITUDE
    # FC = TRACK_FROM_FIX_FROM_DISTANCE
    # FD = TRACK_FROM_FIX_TO_DME_DISTANCE
    # FM = FROM_FIX_TO_MANUAL_TERMINATION
    # HA = HOLD_TO_ALTITUDE
    # HF = HOLD_TO_FIX
    # HM = HOLD_TO_MANUAL_TERMINATION
    # IF = INITIAL_FIX
    # PI = PROCEDURE_TURN
    # RF = CONSTANT_RADIUS_ARC
    # TF = TRACK_TO_FIX
    # VA = HEADING_TO_ALTITUDE_TERMINATION
    # VD = HEADING_TO_DME_DISTANCE_TERMINATION
    # VI = HEADING_TO_INTERCEPT
    # VM = HEADING_TO_MANUAL_TERMINATION
    # VR = HEADING_TO_RADIAL_TERMINATION
    # RX = DIRECT_TO_RUNWAY
    # CX = CIRCLE_TO_LAND
    # TX = STRAIGHT_IN
    # SX = START_OF_PROCEDURE
    # VX = VECTORS
    # CFX = CUSTOM_APP_START
    # CRX = CUSTOM_APP_RUNWAY
    # CDX = CUSTOM_DEP_END
    # CDR = CUSTOM_DEP_RUNWA
    type = Column(String(10), nullable=False)
    arinc_descr_code = Column(String(25))  # ARINC description code 5.17
    # A = IAF, M = MAP,  H = Holding fix, etc. see ARINC-424 spec
    approach_fix_type = Column(String(1))
    # A = At altitude specified in first altitude field.
    # + = Fly at or above altitude1
    # - = Fly at or below altitude1
    # B = At or above to at or below altitudes specified in the first and second "Altitude” fields.
    alt_descriptor = Column(String(10))
    turn_direction = Column(String(10))
    rnp = Column(Float)
    # A = AIRPORT
    # L = LOCALIZER
    # NONE = NONE
    # V = VOR
    # N = NDB
    # TN = TERMINAL_NDB
    # W = WAYPOINT or HEADING_TO_ALT or COURSE_TO_DIST or COURSE_TO_ALT or MANUAL_TERMINATION
    # TW = TERMINAL_WAYPOINT
    # R = RUNWAY
    fix_type = Column(String(25))
    fix_ident = Column(String(5))
    fix_region = Column(String(2))
    fix_airport_ident = Column(String(4))
    fix_lonx = Column(Float)
    fix_laty = Column(Float)
    recommended_fix_type = Column(String(25))
    recommended_fix_ident = Column(String(5))
    recommended_fix_region = Column(String(2))
    recommended_fix_lonx = Column(Float)
    recommended_fix_laty = Column(Float)
    is_flyover = Column(Integer, nullable=False)
    is_true_course = Column(Integer, nullable=False)
    course = Column(Float)  # magnetic from ARINC
    distance = Column(Float)  # Distance from source in NM
    time = Column(Float)  # Only for holds in minute
    theta = Column(Float)  # magnetic course to recommended navaid
    rho = Column(Float)  # distance to recommended navaid in NM
    altitude1 = Column(Float)
    altitude2 = Column(Float)
    speed_limit_type = Column(String(2))
    speed_limit = Column(Integer)
    vertical_angle = Column(Float)

    @property
    def position(self):
        return Position(self.fix_laty, self.fix_lonx)
