from typing import TYPE_CHECKING

from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship, Mapped

from db.init import Base
from .fix import Fix

if TYPE_CHECKING:
    from .airport import Airport


class Ndb(Fix, Base):
    __tablename__ = 'ndb'

    ndb_id = Column(Integer, primary_key=True)
    file_id = Column(Integer, ForeignKey(
        'bgl_file.bgl_file_id'), nullable=False)
    airport_id = Column(Integer, ForeignKey('airport.airport_id'))
    name = Column(String(50))
    frequency = Column(Integer, nullable=False)
    range = Column(Integer)
    mag_var = Column(Float, nullable=False)
    altitude = Column(Integer)

    airport: Mapped['Airport'] = relationship(foreign_keys=[airport_id])
