from scotus.db import DB
from scotus.db.models import Case, Justice, Petitioner, Respondent, Vote, Party
from scotus.config import SCDB_TEST_FILE, TEST_DB
from scotus.db.add import *
from utilities import *

class TestCase():
  @classmethod
  def setup_class(cls):
    database = DB(TEST_DB)
    database.apply([add_justices, lambda x: add_scdb_votes(x, scdb_f=SCDB_TEST_FILE)])
    return
    
  def setup(self):
    self.database = DB(TEST_DB)
    self.session = self.database.Session()
    self.cases_q = self.session.query(Case).filter(Case.scdb_id.in_(["1946-001", "1946-002"]))

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
    database = DB(TEST_DB)
    database.reset()
