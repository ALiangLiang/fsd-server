from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session

engine = create_engine('sqlite:///little_navmap_navigraph.sqlite').connect()
session = Session(engine)

Base = declarative_base()
