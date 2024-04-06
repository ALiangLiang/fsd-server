from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped

from db.init import Base
from messages.Position import Position


class Runway(Base):
    __tablename__ = 'runway'

    runway_id = Column(Integer, primary_key=True)
    airport_id = Column(Integer, ForeignKey(
        'airport.airport_id'), nullable=False)
    primary_end_id = Column(Integer, ForeignKey(
        'runway_end.runway_end_id'), nullable=False)
    secondary_end_id = Column(Integer, ForeignKey(
        'runway_end.runway_end_id'), nullable=False)
    surface = Column(String(15))
    smoothness = Column(Float)
    shoulder = Column(String(15))
    length = Column(Float, nullable=False)
    width = Column(Float, nullable=False)
    heading = Column(Float, nullable=False)
    pattern_altitude = Column(Integer, nullable=False)
    marking_flags = Column(Integer, nullable=False)
    edge_light = Column(String(15))
    center_light = Column(String(15))
    has_center_red = Column(Integer, nullable=False)
    primary_lonx = Column(Float, nullable=False)
    primary_laty = Column(Float, nullable=False)
    secondary_lonx = Column(Float, nullable=False)
    secondary_laty = Column(Float, nullable=False)
    altitude = Column(Integer, nullable=False)
    lonx = Column(Float, nullable=False)
    laty = Column(Float, nullable=False)

    airport: Mapped["Airport"] = relationship(back_populates="runways")
    primary_end = relationship("RunwayEnd", foreign_keys=[primary_end_id])
    secondary_end = relationship("RunwayEnd", foreign_keys=[secondary_end_id])

    @property
    def position(self):
        return Position(self.laty, self.lonx)
