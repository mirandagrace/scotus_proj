import os
from config import DEFAULT_DB, TEST_DB
from models import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# class that provides a single location for the runctions to manage 
class DB(object):
  def __init__(self, test=False):
    if test:
      self.url = TEST_DB
      self.mode = 'test'
    else:
      self.url = DEFAULT_DB
      self.mode = 'production'
    self.engine = create_engine(self.url)
    self.Session = sessionmaker(bind=self.engine)
    return

  def _clear(self):
    Base.metadata.drop_all(self.engine)
    return

  def reset(self, force=False):
    if self.mode == 'production' and not force:
      raise AttributeError, 'If you want to reset the production database you need to set force=True'
    else:
      self._clear()
      self._initialize()
    return
  
  def _initialize(self):
    Base.metadata.create_all(self.engine)
    return
  


