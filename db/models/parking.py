from typing import TYPE_CHECKING

from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey
from sqlalchemy.orm import relationship, Mapped

from db.init import Base
from messages.Position import Position

if TYPE_CHECKING:
    from .airport import Airport


class Parking(Base):
    __tablename__ = 'parking'

    parking_id = Column(Integer, primary_key=True)
    airport_id = Column(Integer, ForeignKey(
        'airport.airport_id'), nullable=False)
    type = Column(String(20))
    pushback = Column(String(5))
    name = Column(String(15))
    number = Column(Integer, nullable=False)
    suffix = Column(String(5))
    airline_codes = Column(Text)
    radius = Column(Float)
    heading = Column(Float)
    has_jetway = Column(Integer, nullable=False)
    lonx = Column(Float, nullable=False)
    laty = Column(Float, nullable=False)

    airport: Mapped['Airport'] = relationship(back_populates='parkings')

    @property
    def position(self):
        return Position(self.laty, self.lonx)
