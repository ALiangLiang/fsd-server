from typing import TYPE_CHECKING

from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship, Mapped

from db.init import Base

if TYPE_CHECKING:
    from .waypoint import Waypoint


class Airway(Base):
    __tablename__ = 'airway'

    airway_id = Column(Integer, primary_key=True)
    airway_name = Column(String(5), nullable=False)
    airway_type = Column(String(15), nullable=False)
    route_type = Column(String(5))
    airway_fragment_no = Column(Integer, nullable=False)
    sequence_no = Column(Integer, nullable=False)
    from_waypoint_id = Column(Integer, ForeignKey(
        'waypoint.waypoint_id'), nullable=False)
    to_waypoint_id = Column(Integer, ForeignKey(
        'waypoint.waypoint_id'), nullable=False)
    direction = Column(String(1))  # B: Backward, F: Forward, N: Both
    minimum_altitude = Column(Integer)
    maximum_altitude = Column(Integer)
    left_lonx = Column(Float, nullable=False)
    top_laty = Column(Float, nullable=False)
    right_lonx = Column(Float, nullable=False)
    bottom_laty = Column(Float, nullable=False)
    from_lonx = Column(Float, nullable=False)
    from_laty = Column(Float, nullable=False)
    to_lonx = Column(Float, nullable=False)
    to_laty = Column(Float, nullable=False)

    from_waypoint: Mapped["Waypoint"] = relationship(
        foreign_keys=[from_waypoint_id])
    to_waypoint: Mapped["Waypoint"] = relationship(
        foreign_keys=[to_waypoint_id])
