from typing import TYPE_CHECKING

from geopy.distance import Distance
from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship, Mapped

from db.init import Base
from messages.Position import Position

if TYPE_CHECKING:
    from .airport import Airport
    from .runway_end import RunwayEnd


class Start(Base):
    __tablename__ = 'start'

    start_id = Column(Integer, primary_key=True)
    airport_id = Column(Integer, ForeignKey(
        'airport.airport_id'), nullable=False)
    runway_end_id = Column(Integer, ForeignKey('runway_end.runway_end_id'))
    runway_name = Column(String(10))
    type = Column(String(10))
    heading = Column(Float, nullable=False)
    number = Column(Integer)
    altitude = Column(Integer, nullable=False)
    lonx = Column(Float, nullable=False)
    laty = Column(Float, nullable=False)

    airport: Mapped['Airport'] = relationship(back_populates='starts')
    runway_end: Mapped['RunwayEnd'] = relationship(back_populates='start')

    @property
    def position(self):
        return Position(self.laty, self.lonx, Distance(feet=self.altitude))
