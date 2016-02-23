from utilities import *
from scotus.items import CaseLoader, VoteLoader, AdvocateLoader, ArgumentLoader, SectionLoader
from scotus.settings import TEST_DB, SCDB_TEST_FILE
from scotus.add import add_justices, add_scdb_votes
from scotus.build import Build
from scotus.db import DB
from scotus.db.models import *


def send_case(session, case_file):
  case_json = load_json(case_file)
  case_item = CaseLoader(case_json).load_case_data()
  case_item.send(session)
  return case_item

def send_case_decision(session, case_item, decision_file):
  decision_json = load_json(decision_file)
  decision_item = CaseLoader(decision_json, item=case_item).load_decision_data()
  decision_item.send(session)
  return decision_item
  
def get_vote(session, justice, docket=None, case_oyez_id=None):
  vote = session.query(Vote).join(Case, Vote.case).join(Justice, Vote.justice).filter(Justice.oyez_id == justice)
  if docket != None:
    vote = vote.filter(Case.docket == docket)
  if case_oyez_id != None:
    vote = vote.filter(Case.oyez_id == case_oyez_id)
  return vote.one_or_none()

def send_vote(session, vote_file, id):
  vote_json = load_json(vote_file)
  vote_item = VoteLoader(vote_json).load_vote_data(id)
  vote_item.send(session)
  return vote_item

def send_advocate(session, advocate_file, case_id):
  advocate_json = load_json(advocate_file)
  advocate_item = AdvocateLoader(advocate_json).load_advocate_data(case_id)
  advocate_item.send(session)
  return advocate_item
  
def send_advocate_from_speaking(session, advocate_file, case_id):
  advocate_json = load_json(advocate_file)
  advocate_item = AdvocateLoader(advocate_json).load_speaking_data(case_id)
  advocate_item.send(session)
  return advocate_item
  
def send_argument(session, transcript_file, case_id):
  argument_json = load_json(transcript_file)
  argument_item = ArgumentLoader(argument_json).load_argument_data(case_id)
  argument_item.send(session)
  return argument_item

def send_section(session, section_file, argument_id, number):
  section_json = load_json(section_file)
  section_item = SectionLoader(section_json).load_section_data(argument_id, number)
  section_item.send(session)
  return section_item

class DBReset(object):
  db = DB(TEST_DB)
  session = None
  
  @classmethod
  def build(cls):
    cls.db.reset()
    build = Build()
    phase_1 = build.add(0, add_justices)
    phase_2 = build.add(1, lambda x: add_scdb_votes(x, scdb_f=SCDB_TEST_FILE), name='add_scdb_votes')
    cls.db.populate(build)
    return cls.db.Session()
    
  ##### CASE FUNCTIONS #####
  
  @classmethod
  def update_case(self):
    case = self.update_case_base()
    return self.update_case_decision(case)
  
  @classmethod
  def update_case_base(self):
    case = send_case(self.session, 'tests/pages/housing.json')
    return case
  
  @classmethod
  def update_case_decision(self, item):
    case = send_case_decision(self.session, item, 'tests/pages/housing_decision.json')
    return case
    
  @classmethod
  def update_case2_base(self):
    case = send_case(self.session, 'tests/pages/search_case.json')
    return case
    
  @classmethod
  def new_case(self):
    case = self.new_case_base()
    return self.new_case_decision(case)
    
  @classmethod
  def new_case_base(self):
    case = send_case(self.session, 'tests/pages/obergefell.json')
    return case
    
  @classmethod
  def new_case_decision(self, item):
    case = send_case_decision(self.session, item, 'tests/pages/obergefell_decision.json')
    return case
    
  ##### VOTE FUNCTIONS #####
  @classmethod
  def update_opinion_joining_only(self):
    return send_vote(self.session,'tests/pages/vote_joining_only.json', 56072)

  @classmethod
  def update_opinion_writing_only(self):
    return send_vote(self.session, 'tests/pages/vote_writing_only.json', 56072)
    
  @classmethod
  def update_vote_writing_only(self):
    return send_vote(self.session, 'tests/pages/kennedy_vote_housing.json', 56072)
    
  @classmethod
  def update_vote_joining_only(self):
    return send_vote(self.session, 'tests/pages/kagan_housing_vote.json', 56072)
    
  @classmethod
  def update_vote(self):
    return send_vote(self.session, 'tests/pages/bryer_vote_search.json', 56132)
  
  @classmethod
  def new_vote_writing_and_joining_multiple(self):
    return send_vote(self.session, 'tests/pages/obergefell_vote_scalia.json', 56149)
  
  @classmethod
  def new_vote_joining_only(self):
    return send_vote(self.session, 'tests/pages/obergefell_ginsburg.json', 56149)
    
  ##### ADVOCATE FUNCTIONS #####
  
  @classmethod
  def advocate_verrilli(self):
    return send_advocate(self.session, 'tests/pages/obergefell_advocate_verilli.json', 56149)
  
  @classmethod
  def update_verrilli(self):
    return send_advocate(self.session, 'tests/pages/verrilli_advocate2.json', 56072)
    
  @classmethod
  def advocate_whalen(self):
    return send_advocate(self.session, 'tests/pages/advocate_whalen.json', 56149)
  
  @classmethod
  def advocate_from_speaking(self):
    return send_advocate_from_speaking(self.session, 'tests/pages/advocate_from_speaking.json', 56072)
    
  @classmethod
  def advocate_update_speaking(self):
    return send_advocate(self.session, 'tests/pages/advocate_update_speaking.json', 56072)
    
  @classmethod
  def advocate_from_speaking2(self):
    return send_advocate_from_speaking(self.session, 'tests/pages/advocate_from_speaking.json', 56072)
    
  ##### ARGUMENT FUNCTIONS #####
  @classmethod
  def new_argument(self):
    return send_argument(self.session, 'tests/pages/obergefell_transcript_1.json', 56149)

  ##### SECTION FUNCTIONS #####
  @classmethod
  def new_section(self):
    return send_section(self.session, 'tests/pages/obergefell_section2.json', 23751, 2)
  
  @classmethod
  def teardown_class(cls):
    cls.session.close()
    DB(TEST_DB).reset()

class TestCaseSender(DBReset):
  
  @classmethod
  def setup_class(cls):
    cls.session = cls.build()
  
  def test_new_case(self):
    case = self.session.query(Case).filter(Case.docket==u"14-556").one_or_none()
    assert_t(case == None)
    self.new_case()
    case = self.session.query(Case).filter(Case.docket==u"14-556").scalar()
    assert_t(len(case.questions) == 2)
    assert_t(case.oyez_id == 56149)
    assert_f(case.prec_alt)
    assert_t(case.facts == u"Groups of same-sex couples sued their relevant state agencies in Ohio, Michigan, Kentucky, and Tennessee to challenge the constitutionality of those states\u0027 bans on same-sex marriage or refusal to recognize legal same-sex marriages that occurred in jurisdictions that provided for such marriages. The plaintiffs in each case argued that the states\u0027 statutes violated the Equal Protection Clause and Due Process Clause of the Fourteenth Amendment, and one group of plaintiffs also brought claims under the Civil Rights Act. In all the cases, the trial court found in favor of the plaintiffs. The U.S. Court of Appeals for the Sixth Circuit reversed and held that the states\u0027 bans on same-sex marriage and refusal to recognize marriages performed in other states did not violate the couples\u0027 Fourteenth Amendment rights to equal protection and due process.")
    
  def test_update_case(self):
    case = self.session.query(Case).filter(Case.docket==u"13-1371").one()
    self.update_case()
    case = self.session.query(Case).filter(Case.docket==u"13-1371").scalar()
    assert_t(len(case.questions) == 1)
    assert_t(case.oyez_id == 56072)
    
class TestVoteSender(DBReset):
  @classmethod
  def setup_class(cls):
    cls.session = cls.build()
    cls.new_case()
    cls.update_case()
    cls.update_case2_base()
    
  def check_vote(self, f, justice_oyez_id, docket=None, case_oyez_id=None, 
                 writing=0, joining=0, new=False, opinion_delta=0, side=None):
    vote = get_vote(self.session, justice_oyez_id, docket=docket, case_oyez_id=case_oyez_id)
    assert_t(vote or new)
    justice = Justice.search_by_oyez_id(self.session, justice_oyez_id)
    a_count = len(justice.authored)
    j_count = len(justice.joined)
    f()
    vote = get_vote(self.session, justice_oyez_id, docket=docket, case_oyez_id=case_oyez_id)
    assert_t(vote)
    if side != None:
      assert_t(vote.vote==side)
    assert_eq(len(justice.authored), a_count+writing)
    assert_eq(len(justice.joined), j_count+joining)
    
  def test_update_vote(self):
    self.check_vote(self.update_vote, 15139, docket=u"13-9972", joining=1, opinion_delta=1)
    
  def test_update_opinion_write_first(self):
    start = self.session.query(Opinion).count()
    self.check_vote(self.update_vote_writing_only, 15113, docket=u"13-1371", writing=1, opinion_delta=1)
    self.check_vote(self.update_vote_joining_only, 15094, docket=u"13-1371", joining=1, opinion_delta=0)
    end = self.session.query(Opinion).count()
    assert start+1 == end
    
  def test_update_opinion_join_first(self):
    self.check_vote(self.update_opinion_joining_only, 15086, docket=u"13-1371", joining=1, opinion_delta=1)
    self.check_vote(self.update_opinion_writing_only, 15068, docket=u"13-1371")
    
    
  def test_new_vote_writing_and_joining_multiple(self):
    self.check_vote(self.new_vote_writing_and_joining_multiple, 15049, case_oyez_id= 56149, 
                    joining=3, writing=1, opinion_delta=4, side=u'minority', new=True)
    
class TestAdvocateSender(DBReset):
  @classmethod
  def setup_class(cls):
    cls.session = cls.build()
    cls.new_case()
    cls.update_case()
    cls.update_case2_base()
    
  def test_new_advocate(self):
    advocate=Advocate.search_for_scraped(self.session, 56185)
    assert_f(advocate)
    self.advocate_whalen()
    advocate=Advocate.search_for_scraped(self.session, 56185)
    assert_t(advocate)
    assert_t(len(advocate.cases)==1)
    advocacy = advocate.case_advocacies[0]
    assert_t(advocacy.side=='respondent')
  
  def test_new_advocate_from_speaking(self):
    advocate=Advocate.search_for_scraped(self.session, 56070)
    assert_f(advocate)
    self.advocate_from_speaking()
    advocate=Advocate.search_for_scraped(self.session, 56070)
    assert_t(advocate)
    assert_t(len(advocate.cases)==1)
    
  def test_update_advocate(self):
    advocate=Advocate.search_for_scraped(self.session, 21656)
    self.advocate_verrilli()
    self.update_verrilli()
    advocate=Advocate.search_for_scraped(self.session, 21656)
    assert_t(advocate)
    assert_t(len(advocate.cases)==2)
    
  def test_update_speaking(self):
    self.advocate_from_speaking2()
    self.advocate_update_speaking()
    advocate=Advocate.search_for_scraped(self.session, 29018)
    assert_t(advocate)
    assert_t(len(advocate.cases)==1)
    advocacy = advocate.case_advocacies[0]
    assert_t(advocacy.side=='respondent')
    
    
class TestTranscriptSenders(DBReset):
  @classmethod
  def setup_class(cls):
    cls.session = cls.build()
    cls.new_case()

  def test_new_argument(self):
    argument_item = self.new_argument()
    argument = Argument.search_by_oyez_id(self.session, 23751)
    assert_t(argument.date)

class TestSectionSenders(DBReset):
  @classmethod
  def setup_class(cls):
    cls.session = cls.build()
    cls.new_case()
    cls.new_argument()

  def test_new_section(self):
    section_item = self.new_section()
    section = Section.search_for_scraped(self.session, section_item['argument_oyez_id'], section_item['number'])
    assert_t(section)





