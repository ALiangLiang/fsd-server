from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship, Mapped

from db.init import Base
from .procedure_leg import ProcedureLeg


class ApproachLeg(ProcedureLeg, Base):
    __tablename__ = 'approach_leg'

    approach_leg_id = Column(Integer, primary_key=True)
    approach_id = Column(Integer, ForeignKey(
        'approach.approach_id'), nullable=False)
    is_missed = Column(Integer, nullable=False)

    approach: Mapped['Approach'] = relationship(back_populates='approach_legs')
