from sqlalchemy import create_engine, Column, Integer, Unicode, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext import baked
from sqlalchemy import bindparam

class IdBase(object):
  id = Column(Integer, primary_key=True, autoincrement=True)


Base = declarative_base(cls=IdBase)
bakery = baked.bakery()

class BuildStatus(Base):
  __tablename__ = 'status'
  name = Column(Unicode(20), nullable=False, unique=True)
  complete = Column(Boolean, nullable=False)

class OyezIdMixin(object):
  oyez_id = Column(Integer, index=True, unique=True) # oyez

