from scotus.db import DB
from scotus.build import Build
from scotus.db.models import Case, Justice, Petitioner, Respondent, Vote, Party
from scotus.settings import SCDB_TEST_FILE, TEST_DB
from scotus.add import *
from utilities import *

class TestCase:
  database = DB(TEST_DB)
  
  @classmethod
  def setup_class(cls):
    cls.database.reset()
    build = Build()
    phase_1 = build.add(0, add_justices)
    phase_2 = build.add(1, lambda x: add_scdb_votes(x, scdb_f=SCDB_TEST_FILE), name='add_scdb_votes')
    cls.database.populate(build)
    cls.session = cls.database.Session()
    return
    
  def setup(self):
    pass
    
  def get_cases(self):
    return self.session.query(Case).filter(Case.scdb_id.in_([u"1946-001", u"1946-002"])).all()

  def test_winner(self):
    for case in self.get_cases():
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
    for case in self.get_cases():
      assert_eq(len(case.questions), 0)

  @classmethod  
  def teardown_class(cls):
    cls.session.close()
    cls.database = DB(TEST_DB)
    cls.database.reset()
