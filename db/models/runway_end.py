from typing import TYPE_CHECKING, Optional

from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import relationship, Mapped
from geopy.distance import Distance
from skspatial.objects import Point, Line, Vector

from db.init import Base
from messages.Position import Position

if TYPE_CHECKING:
    from .approach import Approach
    from .runway import Runway
    from .start import Start
    from .ils import Ils


def position_to_point(position: Position):
    return Point([position.longitude, position.latitude])


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
        primaryjoin='Runway.primary_end_id == RunwayEnd.runway_end_id or Runway.secondary_end_id == RunwayEnd.runway_end_id',
    )
    # approaches: Mapped['RunwayEnd'] = relationship(back_populates='runway_end')
    start: Mapped['Start'] = relationship(back_populates='runway_end')
    approaches: Mapped[list['Approach']] = relationship(
        back_populates='runway_end')
    ils: Mapped[Optional['Ils']] = relationship(back_populates='runway_end')

    @property
    def position(self):
        return Position(self.laty, self.lonx)

    @property
    def touch_down_position(self):
        ils = self.ils
        if ils is None:
            return None

        projection_point = Line.from_points(
            position_to_point(ils.position),
            position_to_point(self.position),
        ).project_point(
            position_to_point(ils.gs_position)
        )
        return Position(projection_point[1], projection_point[0], Distance(feet=ils.gs_altitude))

    @property
    def loc_line(self):
        ils = self.ils
        touch_down_position = self.touch_down_position
        if ils is None or touch_down_position is None:
            return None

        vector2 = Vector.from_points(
            position_to_point(ils.position),
            position_to_point(self.position),
        )
        return Line(
            position_to_point(touch_down_position),
            vector2,
        )
