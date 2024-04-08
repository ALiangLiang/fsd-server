from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.orm import relationship, Mapped

from db.init import Base
from .fix import Fix

if TYPE_CHECKING:
    from .airport import Airport


class Waypoint(Fix, Base):
    __tablename__ = 'waypoint'

    waypoint_id = sa.Column(sa.Integer, primary_key=True)
    file_id = sa.Column(sa.Integer)
    airport_id = sa.Column(sa.Integer, sa.ForeignKey('airport.airport_id'))
    nav_id = sa.Column(sa.Integer)
    artificial = sa.Column(sa.Integer)
    arinc_type = sa.Column(sa.String(4))
    num_victor_airway = sa.Column(sa.Integer)
    num_jet_airway = sa.Column(sa.Integer)
    mag_var = sa.Column(sa.Double)

    airport: Mapped['Airport'] = relationship(
        foreign_keys=[airport_id])
