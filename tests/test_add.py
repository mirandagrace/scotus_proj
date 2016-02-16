# -*- coding: utf-8 -*-
from scotus.db import DB
from scotus.add import *
from scotus.db.models import Case, Justice, Petitioner, Respondent, Vote, Party
from scotus.settings import SCDB_TEST_FILE, TEST_DB
from utilities import *

class TestAdd():
  test_strings = ['"1946-001","1946-001-01","1946-001-01-01","1946-001-01-01-01-01",11/18/1946,1,"329 U.S. 1","67 S. Ct. 6","91 L. Ed. 3","1946 U.S. LEXIS 1724",1946,1301,"Vinson","24","HALLIBURTON OIL WELL CEMENTING CO. v. WALKER et al., DOING BUSINESS AS DEPTHOGRAPH CO.",1/9/1946,10/23/1946,198,,172,,6,,,0,51,6,29,,0,11,2,1,1,3,0,1,1,0,80180,8,2,0,4,,6,600,"35 U.S.C. ยง 33",78,78,1,8,1,86,"HHBurton",2,1,1,1,,\n'
,
                '"2014-040","2014-040-01","2014-040-01-01","2014-040-01-01-01-01",6/25/2015,1,,,,"2015 U.S. LEXIS 4249",2014,1704,"Roberts","13-1371","TEXAS DEPARTMENT OF HOUSING AND COMMUNITY AFFAIRS v. INCLUSIVE COMMUNITIES PROJECT, INC.",1/21/2015,,7,51,192,,1,,,0,120,,25,,0,11,4,2,1,2,0,0,0,0,20040,2,2,0,4,,3,342,"NA",106,106,1,5,4,111,"JGRoberts",2,1,1,1,112,\n']

  
  def setUp(self):
    self.database.reset()
    self.session = self.database.Session()
    
  def __init__(self):
    self.session = None
    self.database = DB(TEST_DB)
   
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

  def test_add_scdb_case(self):
    try:
      for s in self.test_strings:
        add_scdb_case(make_dict(s), self.session)
      self.session.commit()
    except:
      self.session.rollback()
      raise
    assert len(self.session.query(Case).all()) == 2
    assert len(self.session.query(Petitioner).all()) == 2
    assert len(self.session.query(Respondent).all()) == 2
    assert len(self.session.query(Party).all()) == 4
    return

  def test_add_scdb_votes(self):
    try:
      add_justices(self.session)
      self.session.commit()
      add_scdb_votes(self.session, SCDB_TEST_FILE)
      self.session.commit()
    except:
      self.session.rollback()
      raise
    return

  def tearDown(self):
    self.session.close()
    self.database.reset()
    