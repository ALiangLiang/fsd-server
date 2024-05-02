from typing import TYPE_CHECKING

from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship, Mapped

from db.init import Base
from messages.Position import Position

if TYPE_CHECKING:
    from .runway_end import RunwayEnd


class Ils(Base):
    __tablename__ = 'ils'

    ils_id = Column(Integer, primary_key=True)
    ident = Column(String(5))
    name = Column(String(50))
    region = Column(String(2))
    type = Column(String(1))
    perf_indicator = Column(String(10))
    provider = Column(String(10))
    frequency = Column(Integer)
    range = Column(Integer)
    mag_var = Column(Float, nullable=False)
    has_backcourse = Column(Integer, nullable=False)
    dme_range = Column(Integer)
    dme_altitude = Column(Integer)  # Feet if available - otherwise null
    dme_lonx = Column(Float)
    dme_laty = Column(Float)
    # Glideslope range in NM if available - otherwise null
    gs_range = Column(Integer)
    # Glideslope pitch in degree or null if not available
    gs_pitch = Column(Float)
    # Glideslope altitude - feet or null if not available
    gs_altitude = Column(Integer)
    gs_lonx = Column(Float)
    gs_laty = Column(Float)
    loc_runway_end_id = Column(Integer, ForeignKey('runway_end.runway_end_id'))
    loc_airport_ident = Column(String(4))
    loc_runway_name = Column(String(10))
    loc_heading = Column(Float)
    loc_width = Column(Float)
    end1_lonx = Column(Float)
    end1_laty = Column(Float)
    end_mid_lonx = Column(Float)
    end_mid_laty = Column(Float)
    end2_lonx = Column(Float)
    end2_laty = Column(Float)
    altitude = Column(Integer, nullable=False)
    lonx = Column(Float, nullable=False)
    laty = Column(Float, nullable=False)

    runway_end: Mapped['RunwayEnd'] = relationship(back_populates='ils')

    @property
    def position(self):
        return Position(self.laty, self.lonx)

    @property
    def gs_position(self):
        return Position(self.gs_laty, self.gs_lonx)

    @property
    def dme_position(self):
        return Position(self.dme_laty, self.dme_lonx)

    @property
    def end1_position(self):
        return Position(self.end1_laty, self.end1_lonx)

    @property
    def end_mid_position(self):
        return Position(self.end_mid_laty, self.end_mid_lonx)

    @property
    def end2_position(self):
        return Position(self.end2_laty, self.end2_lonx)
