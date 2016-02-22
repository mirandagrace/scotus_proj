from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from contextlib import contextmanager
from .models.base import Base

# class that provides a database management interface
class DB:
  def __init__(self, url):
    self.url = url
    self.Base = Base
    self.engine = create_engine(self.url)
    self.Session = sessionmaker(bind=self.engine)
    return
    
  def populate(self, build):
    session = self.Session()
    try:
      build.run(session)
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
      

    