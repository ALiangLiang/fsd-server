from typing import List, TYPE_CHECKING

from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped

from db.init import Base
from messages.Position import Position

if TYPE_CHECKING:
    from .runway import Runway
    from .approach import Approach
    from .ndb import Ndb


class Airport(Base):
    __tablename__ = 'airport'

    airport_id = Column(Integer, primary_key=True)
    file_id = Column(Integer, ForeignKey(
        'bgl_file.bgl_file_id'), nullable=False)
    ident = Column(String(10), nullable=False)
    icao = Column(String(10))
    iata = Column(String(10))
    faa = Column(String(10))
    local = Column(String(10))
    name = Column(String(50), nullable=False)
    city = Column(String(50))
    state = Column(String(50))
    country = Column(String(50))
    region = Column(String(4))
    flatten = Column(Integer)
    type = Column(Integer)
    fuel_flags = Column(Integer, nullable=False)
    has_avgas = Column(Integer, nullable=False)
    has_jetfuel = Column(Integer, nullable=False)
    has_tower_object = Column(Integer, nullable=False)
    tower_frequency = Column(Integer)
    atis_frequency = Column(Integer)
    awos_frequency = Column(Integer)
    asos_frequency = Column(Integer)
    unicom_frequency = Column(Integer)
    is_closed = Column(Integer, nullable=False)
    is_military = Column(Integer, nullable=False)
    is_addon = Column(Integer, nullable=False)
    num_com = Column(Integer, nullable=False)
    num_parking_gate = Column(Integer, nullable=False)
    num_parking_ga_ramp = Column(Integer, nullable=False)
    num_parking_cargo = Column(Integer, nullable=False)
    num_parking_mil_cargo = Column(Integer, nullable=False)
    num_parking_mil_combat = Column(Integer, nullable=False)
    num_approach = Column(Integer, nullable=False)
    num_runway_hard = Column(Integer, nullable=False)
    num_runway_soft = Column(Integer, nullable=False)
    num_runway_water = Column(Integer, nullable=False)
    num_runway_light = Column(Integer, nullable=False)
    num_runway_end_closed = Column(Integer, nullable=False)
    num_runway_end_vasi = Column(Integer, nullable=False)
    num_runway_end_als = Column(Integer, nullable=False)
    num_runway_end_ils = Column(Integer)
    num_apron = Column(Integer, nullable=False)
    num_taxi_path = Column(Integer, nullable=False)
    num_helipad = Column(Integer, nullable=False)
    num_jetway = Column(Integer, nullable=False)
    num_starts = Column(Integer, nullable=False)
    longest_runway_length = Column(Integer, nullable=False)
    longest_runway_width = Column(Integer, nullable=False)
    longest_runway_heading = Column(Float, nullable=False)
    longest_runway_surface = Column(String(15))
    num_runways = Column(Integer, nullable=False)
    largest_parking_ramp = Column(String(20))
    largest_parking_gate = Column(String(20))
    rating = Column(Integer, nullable=False)
    is_3d = Column(Integer, nullable=False)
    scenery_local_path = Column(String(250))
    bgl_filename = Column(String(300))
    left_lonx = Column(Float, nullable=False)
    top_laty = Column(Float, nullable=False)
    right_lonx = Column(Float, nullable=False)
    bottom_laty = Column(Float, nullable=False)
    mag_var = Column(Float, nullable=False)
    tower_altitude = Column(Integer)
    tower_lonx = Column(Float)
    tower_laty = Column(Float)
    transition_altitude = Column(Float)
    transition_level = Column(Float)
    altitude = Column(Integer, nullable=False)
    lonx = Column(Float, nullable=False)
    laty = Column(Float, nullable=False)

    runways: Mapped[List["Runway"]] = relationship(back_populates="airport")
    approaches: Mapped[List["Approach"]] = relationship(
        back_populates="airport")
    ndb: Mapped[List["Ndb"]] = relationship(back_populates="airport")

    @property
    def position(self):
        return Position(self.laty, self.lonx)
