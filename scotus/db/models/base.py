from sqlalchemy import create_engine, Column, Integer, Unicode, Boolean
from sqlalchemy.ext.declarative import declarative_base

class IdBase(object):
    id = Column(Integer, primary_key=True, autoincrement=True)

Base = declarative_base(cls=IdBase)

class BuildStatus(Base):
  __tablename__ = 'status'
  name = Column(Unicode(20), nullable=False, unique=True)
  complete = Column(Boolean, nullable=False)