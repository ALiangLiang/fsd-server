import sqlalchemy as sa

from db.init import Base
from messages.Position import Position


class Vor(Base):
    __tablename__ = 'vor'

    vor_id = sa.Column(sa.Integer, primary_key=True)
    file_id = sa.Column(sa.Integer)
    ident = sa.Column(sa.String(5))
    name = sa.Column(sa.String(50))
    region = sa.Column(sa.String(2))
    airport_id = sa.Column(sa.Integer)
    airport_ident = sa.Column(sa.String(4))
    type = sa.Column(sa.String(15))
    frequency = sa.Column(sa.Integer)
    channel = sa.Column(sa.String(5))
    range = sa.Column(sa.Integer)
    mag_var = sa.Column(sa.Double)
    dme_only = sa.Column(sa.Integer)
    dme_altitude = sa.Column(sa.Integer)
    dme_lonx = sa.Column(sa.Double)
    dme_laty = sa.Column(sa.Double)
    altitude = sa.Column(sa.Integer)
    lonx = sa.Column(sa.Double)
    laty = sa.Column(sa.Double)

    @property
    def position(self):
        return Position(self.laty, self.lonx)
