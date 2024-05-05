from sqlalchemy import Column, Integer, LargeBinary

from db.init import Base

class MagDecl(Base):
    __tablename__ = 'magdecl'

    magdecl_id = Column(Integer, primary_key=True)
    reference_time = Column(Integer, nullable=False)
    mag_var = Column(LargeBinary)
