import sqlalchemy as sa

from db.init import Base
from messages.Position import Position


class Waypoint(Base):
    __tablename__ = 'waypoint'

    waypoint_id = sa.Column(sa.Integer, primary_key=True)
    file_id = sa.Column(sa.Integer)
    nav_id = sa.Column(sa.Integer)
    ident = sa.Column(sa.String(5))
    region = sa.Column(sa.String(2))
    airport_id = sa.Column(sa.Integer)
    airport_ident = sa.Column(sa.String(4))
    artificial = sa.Column(sa.Integer)
    type = sa.Column(sa.String(15))
    arinc_type = sa.Column(sa.String(4))
    num_victor_airway = sa.Column(sa.Integer)
    num_jet_airway = sa.Column(sa.Integer)
    mag_var = sa.Column(sa.Double)
    lonx = sa.Column(sa.Double)
    laty = sa.Column(sa.Double)

    @property
    def position(self):
        return Position(self.laty, self.lonx)
