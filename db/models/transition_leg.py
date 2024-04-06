from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship, Mapped

from db.init import Base
from .procedure_leg import ProcedureLeg


class TransitionLeg(ProcedureLeg, Base):
    __tablename__ = 'transition_leg'

    transition_leg_id = Column(Integer, primary_key=True)
    transition_id = Column(Integer, ForeignKey(
        'transition.transition_id'), nullable=False)

    transition: Mapped['Transition'] = relationship(
        foreign_keys=[transition_id])
