from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.orm import relationship, Mapped

from db.init import Base
from .fix import Fix

if TYPE_CHECKING:
    from .airport import Airport


class Vor(Fix, Base):
    __tablename__ = 'vor'

    vor_id = sa.Column(sa.Integer, primary_key=True)
    file_id = sa.Column(sa.Integer)
    airport_id = sa.Column(sa.Integer, sa.ForeignKey('airport.airport_id'))
    name = sa.Column(sa.String(50))
    frequency = sa.Column(sa.Integer)
    channel = sa.Column(sa.String(5))
    range = sa.Column(sa.Integer)
    mag_var = sa.Column(sa.Double)
    dme_only = sa.Column(sa.Integer)
    dme_altitude = sa.Column(sa.Integer)
    dme_lonx = sa.Column(sa.Double)
    dme_laty = sa.Column(sa.Double)
    altitude = sa.Column(sa.Integer)

    airport: Mapped['Airport'] = relationship(foreign_keys=[airport_id])
