from ..db import DB
from ..scdb.ingest import *
from ..models import Case, Justice, Petitioner, Respondent, Vote, Party
from ..config import SCDB_TEST_FILE
from utilities import *

def setup_module():
  database.reset()
  database.populate()
  return

class TestCase():
  @classmethod
  def setup_class(cls):
    cls.session = database.Session()
    cls.cases_q = cls.session.query(Case).filter(Case.scdb_id.in_(["1946-001", "1946-002"]))
    return

  def test_winner(self):
    for case in self.cases_q.all():
      if case.winning_side == 'petitioner':
        yield assert_eq, case.winner.id, case.petitioner.id
        yield assert_t, case.petitioner.winner
        yield assert_f, case.respondent.winner
      elif case.winning_side == 'respondent':
        yield assert_eq, case.winner.id, case.respondent.id
        yield assert_t, case.respondent.winner
        yield assert_f, case.petitioner.winner
      else:
        yield assert_eq, case.winner, None

  def test_questions(self):
    for case in self.cases_q.all():
      assert_eq(len(case.questions), 0)

  @classmethod  
  def teardown_class(cls):
    cls.session.close()

def teardown_module():
  database.reset()
  return
    