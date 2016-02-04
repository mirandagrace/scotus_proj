from db import DB
from scdb.ingest import *
from models import Case, Justice, Petitioner, Respondent, Vote

class TestIngestSCDB():
  def setUp(self):
    self.database.reset()
    self.session = self.database.Session()
    
  def __init__(self):
    self.database = DB(test=True)
   
  def test_add_justices(self):
    try:
      add_justices(self.session)
      self.session.commit()
    except:
      self.session.rollback()
      raise 
    num_added = len(self.session.query(Justice).all())
    expected = 111
    assert num_added == expected, 'added {}, expected {}'.format(num_added, str(expected))
    
  def tearDown(self):
    self.session.close()
    self.database.reset()
    