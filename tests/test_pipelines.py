from utilities import *
from scotus.pipelines import *
from scotus.items import CaseLoader, VoteLoader
from scotus.settings import TEST_DB, SCDB_TEST_FILE
from scotus.add import add_justices, add_scdb_votes
from scotus.build import Build

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
    self.pipeline = OyezPipeline(DB(TEST_DB))
    self.pipeline.open_session()

  def test_send_new_case(self):
    case = self.pipeline.session.query(Case).filter(Case.docket==u"14-556").one_or_none()
    assert_t(case == None)
    case = make_case('tests/pages/obergefell.json', 'tests/pages/obergefell_decision.json')
    self.pipeline.process_item(case, None)
    case = self.pipeline.session.query(Case).filter(Case.docket==u"14-556").scalar()
    assert_t(len(case.questions) == 2)
    assert_t(case.oyez_id == 56149)
    assert_t(case.facts == u"Groups of same-sex couples sued their relevant state agencies in Ohio, Michigan, Kentucky, and Tennessee to challenge the constitutionality of those states\u0027 bans on same-sex marriage or refusal to recognize legal same-sex marriages that occurred in jurisdictions that provided for such marriages. The plaintiffs in each case argued that the states\u0027 statutes violated the Equal Protection Clause and Due Process Clause of the Fourteenth Amendment, and one group of plaintiffs also brought claims under the Civil Rights Act. In all the cases, the trial court found in favor of the plaintiffs. The U.S. Court of Appeals for the Sixth Circuit reversed and held that the states\u0027 bans on same-sex marriage and refusal to recognize marriages performed in other states did not violate the couples\u0027 Fourteenth Amendment rights to equal protection and due process.")

  def test_send_existing_case(self):
    case = self.pipeline.session.query(Case).filter(Case.docket==u"13-1371").one()
    case = make_case('tests/pages/housing.json', 'tests/pages/housing_decision.json')
    self.pipeline.process_item(case, None)
    case = self.pipeline.session.query(Case).filter(Case.docket==u"13-1371").scalar()
    assert_t(len(case.questions) == 1)
    assert_t(case.oyez_id == 56072)

  def test_vote_joining_only(self):
    self.test_send_existing_case()
    vote_query = self.pipeline.session.query(Vote)
    vote_query = vote_query.join(Case, Vote.case).join(Justice, Vote.justice)
    vote_query = vote_query.filter(Case.docket == u"13-1371").filter(Justice.oyez_id == 15086).one()
    j = vote_query.justice
    vote = make_vote('tests/pages/vote_joining_only.json', 56072)
    self.pipeline.process_item(vote, None)
    justice = Justice.search_by_oyez_id(self.pipeline.session, 15086)
    assert_t(len(justice.authored)==0)
    assert_t(len(justice.joined)==1)


  def test_vote_writing_only(self):
    self.test_send_existing_case()
    vote_query = self.pipeline.session.query(Vote).join(Case, Vote.case).join(Justice, Vote.justice)
    vote_query = vote_query.filter(Case.docket == u"13-1371", Justice.oyez_id == 15068).one()
    print vote_query.justice
    assert_t(len(vote_query.justice.joined)==0)
    vote = make_vote('tests/pages/writing_only.json', 56072)
    self.pipeline.process_item(vote, None)
    j = Justice.search_by_oyez_id(self.pipeline.session, 15068)
    print j.joined
    print j.authored
    assert_t(len(j.authored)==1)
    assert_t(len(j.joined)==0)
    
  def teardown(self):
    self.pipeline.close_session()
    DB(TEST_DB).reset()
    
  @classmethod
  def teardown_class(cls):
    DB(TEST_DB).reset()
