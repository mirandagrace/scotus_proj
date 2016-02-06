from ..db import DB
from ..scdb.ingest import *
from ..models import Case, Justice, Petitioner, Respondent, Vote, Party
from ..config import SCDB_TEST_FILE
from utilities import *

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
    expected = 112
    assert num_added == expected, 'added {}, expected {}'.format(num_added, str(expected))
    return

  def test_add_case(self):
    try:
      add_justices(self.session)
      for s in test_strings:
        add_case(make_dict(s), self.session)
      self.session.commit()
    except:
      self.session.rollback()
      raise
    assert len(self.session.query(Case).all()) == 2
    assert len(self.session.query(Petitioner).all()) == 2
    assert len(self.session.query(Respondent).all()) == 2
    assert len(self.session.query(Party).all()) == 4
    return

  def test_add_votes(self):
    try:
      add_justices(self.session)
      self.session.commit()
      add_votes(self.session, f=SCDB_TEST_FILE, print_progress=True)
      self.session.commit()
    except:
      self.session.rollback()
      raise
    return

    
  def tearDown(self):
    self.session.close()
    self.database.reset()
    