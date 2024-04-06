from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship, Mapped

from db.init import Base


class Transition(Base):
    __tablename__ = 'transition'

    transition_id = Column(Integer, primary_key=True)
    approach_id = Column(Integer, ForeignKey(
        'approach.approach_id'), nullable=False)
    type = Column(String(25), nullable=False)
    fix_type = Column(String(25))
    fix_ident = Column(String(5))
    fix_region = Column(String(2))
    fix_airport_ident = Column(String(4))
    aircraft_category = Column(String(4))
    altitude = Column(Integer)
    dme_ident = Column(String(5))
    dme_region = Column(String(2))
    dme_airport_ident = Column(String(4))
    dme_radial = Column(Float)
    dme_distance = Column(Integer)

    approach: Mapped['Approach'] = relationship(foreign_keys=[approach_id])
    transition_legs: Mapped[list['TransitionLeg']] = relationship(back_populates='transition')
