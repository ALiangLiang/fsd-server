from sqlalchemy import Column, String, Float

from messages.Position import Position


class Fix:
    ident = Column(String(5))
    region = Column(String(2))
    airport_ident = Column(String(4))
    type = Column(String(15))
    lonx = Column(Float, nullable=False)
    laty = Column(Float, nullable=False)

    @property
    def position(self):
        return Position(self.laty, self.lonx)
