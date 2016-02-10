from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from contextlib import contextmanager
from .add import add_justices, add_scdb_votes
from .models.base import Base

# class that provides a single location for the runctions to manage 
class DB:
  def __init__(self, url):
    self.url = url
    self.Base = Base
    self.engine = create_engine(self.url)
    self.Session = sessionmaker(bind=self.engine)
    return
    
  def apply(self, transactions):
    with self.session_scope() as session:
      for transaction in transactions:
        transaction(session)
        session.commit()
    return
    
  def build(self):
    with session_scope() as session:
      add_justices(session)
      session.commit()
      add_scdb_votes(session)
      session.commit()
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
    
  @contextmanager
  def session_scope(self):
    """Provide a transactional scope around a series of operations."""
    session = self.Session()
    try:
      yield session
      session.commit()
    except:
      session.rollback()
      raise
    finally:
      session.close()