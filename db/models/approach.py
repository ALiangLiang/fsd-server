from typing import List, TYPE_CHECKING

from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship, Mapped

from db.init import Base

if TYPE_CHECKING:
    from .airport import Airport
    from .approach_leg import ApproachLeg
    from .transition import Transition


class Approach(Base):
    __tablename__ = 'approach'

    approach_id = Column(Integer, primary_key=True)
    airport_id = Column(Integer, ForeignKey(
        'airport.airport_id'), nullable=False)
    runway_end_id = Column(Integer, ForeignKey('runway_end.runway_end_id'))
    arinc_name = Column(String(6))
    airport_ident = Column(String(4))
    runway_name = Column(String(10))
    type = Column(String(25), nullable=False)
    suffix = Column(String(1))
    has_gps_overlay = Column(Integer, nullable=False)
    has_vertical_angle = Column(Integer)
    has_rnp = Column(Integer)
    fix_type = Column(String(25))
    fix_ident = Column(String(5))
    fix_region = Column(String(2))
    fix_airport_ident = Column(String(4))
    aircraft_category = Column(String(4))
    altitude = Column(Integer)
    heading = Column(Float)
    missed_altitude = Column(Integer)

    airport: Mapped[List["Airport"]] = relationship(
        back_populates="approaches")
    # runway_end: Mapped["RunwayEnd"] = relationship(back_populates="approaches")
    approach_legs: Mapped[List["ApproachLeg"]
                          ] = relationship(back_populates="approach")
    transitions: Mapped[List['Transition']] = relationship(
        back_populates='approach')
