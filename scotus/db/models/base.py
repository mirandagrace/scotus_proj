from sqlalchemy import create_engine, Column, Integer, Unicode, Boolean
from sqlalchemy.ext.declarative import declarative_base

class IdBase(object):
    id = Column(Integer, primary_key=True, autoincrement=True)

Base = declarative_base(cls=IdBase)

class Status(Base):
  __tablename__ = 'status'
  name = Column(Unicode(20))
  complete = Column(Boolean, nullable=False)