from scotus.db import DB
from scotus.build import Build
from scotus.db.models import Case, Justice, Petitioner, Respondent, Vote, Party, Citation
from scotus.settings import SCDB_TEST_FILE, TEST_DB
from scotus.add import *
from utilities import *

def test_citation_eq():
  c1 = Citation(volume=300, page=1)
  c2 = Citation(volume=300, page=5)
  c3 = Citation(volume=300, page=1)
  c4 = Citation(volume=301, page=1)
  assert_t(c3 == c1)
  assert_f(c1==c2)
  assert_f(c4==c1)
  
def test_citation_neq():
  c1 = Citation(volume=300, page=1)
  c2 = Citation(volume=300, page=5)
  c3 = Citation(volume=300, page=1)
  c4 = Citation(volume=301, page=1)
  assert_f(c3 != c1)
  assert_t(c1!=c2)
  assert_t(c4!=c1)

class TestModels:
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

  def test_case_winner(self):
    for case in self.get_cases():
      if case.winning_side == 'petitioner':
        assert_eq(case.winner.id, case.petitioner.id)
        assert_t(case.petitioner.winner)
        assert_f(case.respondent.winner)
      elif case.winning_side == 'respondent':
        assert_eq(case.winner.id, case.respondent.id)
        assert_t(case.respondent.winner)
        assert_f(case.petitioner.winner)
      else:
        assert_eq(case.winner, None)
        
  def test_case_loser(self):
    for case in self.get_cases():
      if case.losing_side == 'petitioner':
        assert_eq(case.loser.id, case.petitioner.id)
        assert_f(case.petitioner.winner)
        assert_t(case.respondent.winner)
      elif case.losing_side == 'respondent':
        assert_eq(case.loser.id, case.respondent.id)
        assert_f(case.respondent.winner)
        assert_t(case.petitioner.winner)
      else:
        yield assert_eq, case.loser, None

  def test_questions(self):
    for case in self.get_cases():
      assert_eq(len(case.questions), 0)

  @classmethod  
  def teardown_class(cls):
    cls.session.close()
    cls.database = DB(TEST_DB)
    cls.database.reset()
