from utilities import *
from scotus.items import CaseLoader, VoteLoader, AdvocateLoader
from scotus.settings import TEST_DB, SCDB_TEST_FILE
from scotus.add import add_justices, add_scdb_votes
from scotus.build import Build
from scotus.db import DB
from scotus.db.models import *

def make_case(case_file, decision_file):
  case_json = load_json(case_file)
  case_item = CaseLoader(case_json).load_case_data()
  decision_json = load_json(decision_file)
  decision_item = CaseLoader(decision_json, item=case_item).load_decision_data()
  return case_item

def make_vote(vote_file, id):
  vote_json = load_json(vote_file)
  vote_item = VoteLoader(vote_json).load_vote_data(id)
  return vote_item

def make_advocate(advocate_file, case_id):
  advocate_json = load_json(advocate_file)
  advocate_item = AdvocateLoader(advocate_json).load_advocate_data(case_id)
  return advocate_item

class TestPipelines(object):
  #@classmethod
  def setup(cls):
    db = DB(TEST_DB)
    db.reset()
    build = Build()
    phase_1 = build.add(0, add_justices)
    phase_2 = build.add(1, lambda x: add_scdb_votes(x, scdb_f=SCDB_TEST_FILE), name='add_scdb_votes')
    db.populate(build)

  def __init__(self):
    self.db = DB(TEST_DB)
    self.session = self.db.Session()

  def send_case(self, case_file, decision_file):
    case = make_case(case_file, decision_file)
    case.send(self.session)

  def update_case(self):
    self.send_case('tests/pages/housing.json', 'tests/pages/housing_decision.json')

  def new_case(self):
    self.send_case('tests/pages/obergefell.json', 'tests/pages/obergefell_decision.json')

  def test_new_case(self):
    case = self.session.query(Case).filter(Case.docket==u"14-556").one_or_none()
    assert_t(case == None)
    self.new_case()
    case = self.session.query(Case).filter(Case.docket==u"14-556").scalar()
    assert_t(len(case.questions) == 2)
    assert_t(case.oyez_id == 56149)
    assert_t(case.facts == u"Groups of same-sex couples sued their relevant state agencies in Ohio, Michigan, Kentucky, and Tennessee to challenge the constitutionality of those states\u0027 bans on same-sex marriage or refusal to recognize legal same-sex marriages that occurred in jurisdictions that provided for such marriages. The plaintiffs in each case argued that the states\u0027 statutes violated the Equal Protection Clause and Due Process Clause of the Fourteenth Amendment, and one group of plaintiffs also brought claims under the Civil Rights Act. In all the cases, the trial court found in favor of the plaintiffs. The U.S. Court of Appeals for the Sixth Circuit reversed and held that the states\u0027 bans on same-sex marriage and refusal to recognize marriages performed in other states did not violate the couples\u0027 Fourteenth Amendment rights to equal protection and due process.")

  def test_update_case(self):
    case = self.session.query(Case).filter(Case.docket==u"13-1371").one()
    self.update_case()
    case = self.session.query(Case).filter(Case.docket==u"13-1371").scalar()
    assert_t(len(case.questions) == 1)
    assert_t(case.oyez_id == 56072)

  def get_vote(self, justice, docket=None, case_oyez_id=None):
    vote = self.session.query(Vote).join(Case, Vote.case).join(Justice, Vote.justice).filter(Justice.oyez_id == justice)
    if docket != None:
      vote = vote.filter(Case.docket == docket)
    if case_oyez_id != None:
      vote = vote.filter(Case.oyez_id == case_oyez_id)
    return vote.one_or_none()

  def send_vote(self, vote_file, id):
    vote = make_vote(vote_file, id)
    vote.send(self.session)

  def update_vote_joining_only(self):
    self.send_vote('tests/pages/vote_joining_only.json', 56072)

  def update_vote_writing_only(self):
    self.send_vote('tests/pages/writing_only.json', 56072)

  def new_vote_writing_and_joining_multiple(self):
    self.send_vote('tests/pages/obergefell_vote_scalia.json', 56149)

  def new_vote_joining_only(self):
    self.send_vote('tests/pages/obergefell_ginsburg.json', 56149)

  def test_update_vote_joining_only(self):
    self.update_case()
    vote = self.get_vote(15086, docket=u"13-1371")
    assert_t(vote)
    justice = vote.justice
    assert_t(len(justice.authored)==0)
    assert_t(len(justice.joined)==0)
    self.update_vote_joining_only()
    justice = Justice.search_by_oyez_id(self.session, 15086)
    assert_t(len(justice.authored)==0)
    assert_t(len(justice.joined)==1)

  def test_update_vote_writing_only(self):
    self.update_case()    
    vote = self.get_vote(15068, docket=u"13-1371")
    assert_t(vote)
    assert_t(len(vote.justice.joined)==0)
    assert_t(len(vote.justice.authored)==0)
    self.update_vote_writing_only()
    j = Justice.search_by_oyez_id(self.session, 15068)
    assert_t(len(j.authored)==1)
    assert_t(len(j.joined)==0)

  def test_new_vote_joining_only(self):
    self.new_case()
    vote = self.get_vote(15084, case_oyez_id=56149)
    assert_f(vote)
    self.new_vote_joining_only()
    print self.session.query(Vote).join(Case, Vote.case).join(Justice, Vote.justice).filter(Case.oyez_id==56149).all()
    vote = self.get_vote(15084, case_oyez_id=56149)
    assert_t(vote)
    j = vote.justice
    assert_t(vote.vote == u'majority')
    assert_t(len(j.joined) == 1)
    assert_t(len(j.authored) == 0)

  def test_new_vote_writing_and_joining_multiple(self):
    self.new_case()
    vote = self.get_vote(15049, case_oyez_id= 56149)
    assert_f(vote)
    self.new_vote_writing_and_joining_multiple()
    vote = self.get_vote(15049, case_oyez_id=56149)
    assert_t(vote)
    j = vote.justice
    assert_t(vote.vote == u'minority')
    assert_t(len(j.joined) == 3)
    assert_t(len(j.authored) == 1)
    assert_t(j.authored[0].kind == 'dissent')

  def send_advocate(self, advocate_file, case_id):
    advocate = make_advocate(advocate_file, case_id)
    advocate.send(self.session)

  def new_advocate(self):
    self.send_advocate('tests/pages/obergefell_advocate_kneedler.json', 56149)

  def update_advocate(self):
    

  def test_new_advocate(self):
    self.new_case()
    advocate=Advocate.search_for_scraped(self.session, 22617)
    assert_f(advocate)
    self.new_advocate()
    advocate=Advocate.search_for_scraped(self.session, 22617)
    assert_t(advocate)
    assert_t(len(advocate.cases)==1)

  def teardown(self):
    self.session.close()
    DB(TEST_DB).reset()
    
  @classmethod
  def teardown_class(cls):
    DB(TEST_DB).reset()