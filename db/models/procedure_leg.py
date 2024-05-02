from sqlalchemy import Column, Integer, String, Float

from messages.Position import Position


class ProcedureLeg:
    type = Column(String(10), nullable=False)
    arinc_descr_code = Column(String(25))
    approach_fix_type = Column(String(1))
    alt_descriptor = Column(String(10))
    turn_direction = Column(String(10))
    rnp = Column(Float)
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
