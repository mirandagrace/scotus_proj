from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from contextlib import contextmanager
from .models.base import Base

# class that provides a database management interface
class DB:
  def __init__(self, url, build=None):
    self.url = url
    self.Base = Base
    self.engine = create_engine(self.url)
    self.Session = sessionmaker(bind=self.engine)
    self.build=build
    return
    
  def populate(self, build=None):
    session = self.Session()
    if build != None:
      self.build = build
    try:
      self.build.run(session)
    except:
      raise
    finally:
      session.close()
    return
    
  def update(self):
    session = self.Session()
    try:
      self.build.run(session)
    except:
      raise
    finally:
      session.close()
    return

  def drop_all(self):
    self.Base.metadata.drop_all(self.engine)
    return

  def reset(self):
    self.drop_all()
    self.create_all()
    return
  
  def create_all(self):
    self.Base.metadata.create_all(self.engine)
    return
      

    