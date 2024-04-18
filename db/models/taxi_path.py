from typing import TYPE_CHECKING

from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship, Mapped

from db.init import Base
from messages.Position import Position

if TYPE_CHECKING:
    from .airport import Airport


class TaxiPath(Base):
    __tablename__ = 'taxi_path'

    taxi_path_id = Column(Integer, primary_key=True)
    airport_id = Column(Integer, ForeignKey(
        'airport.airport_id'), nullable=False)
    type = Column(String(15))
    surface = Column(String(15))
    width = Column(Float, nullable=False)
    name = Column(String(20))
    is_draw_surface = Column(Integer, nullable=False)
    is_draw_detail = Column(Integer, nullable=False)
    start_type = Column(String(15))
    start_dir = Column(String(15))
    start_lonx = Column(Float, nullable=False)
    start_laty = Column(Float, nullable=False)
    end_type = Column(String(15))
    end_dir = Column(String(15))
    end_lonx = Column(Float, nullable=False)
    end_laty = Column(Float, nullable=False)

    airport: Mapped['Airport'] = relationship(back_populates='taxi_paths')

    @property
    def start_position(self):
        return Position(self.start_laty, self.start_lonx)

    @property
    def end_position(self):
        return Position(self.end_laty, self.end_lonx)
