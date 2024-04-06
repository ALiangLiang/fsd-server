from typing import List

from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import relationship, backref, Mapped

from db.init import Base
from messages.Position import Position


class RunwayEnd(Base):
    __tablename__ = 'runway_end'

    runway_end_id = Column(Integer, primary_key=True)
    name = Column(String(10), nullable=False)
    end_type = Column(String(1), nullable=False)
    offset_threshold = Column(Float, nullable=False)
    blast_pad = Column(Float, nullable=False)
    overrun = Column(Float, nullable=False)
    left_vasi_type = Column(String(15))
    left_vasi_pitch = Column(Float)
    right_vasi_type = Column(String(15))
    right_vasi_pitch = Column(Float)
    has_closed_markings = Column(Integer, nullable=False)
    has_stol_markings = Column(Integer, nullable=False)
    is_takeoff = Column(Integer, nullable=False)
    is_landing = Column(Integer, nullable=False)
    is_pattern = Column(String(10), nullable=False)
    app_light_system_type = Column(String(15))
    has_end_lights = Column(Integer, nullable=False)
    has_reils = Column(Integer, nullable=False)
    has_touchdown_lights = Column(Integer, nullable=False)
    num_strobes = Column(Integer, nullable=False)
    ils_ident = Column(String(10))
    heading = Column(Float, nullable=False)
    altitude = Column(Integer)
    lonx = Column(Float, nullable=False)
    laty = Column(Float, nullable=False)

    runway: Mapped['Runway'] = relationship(
        primaryjoin="Runway.primary_end_id == RunwayEnd.runway_end_id", back_populates='primary_end', uselist=False)
    # approaches: Mapped["RunwayEnd"] = relationship(
    #     back_populates="runway_end")

    @ property
    def position(self):
        return Position(self.laty, self.lonx)
