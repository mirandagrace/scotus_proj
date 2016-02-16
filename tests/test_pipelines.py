from utilities import *
from scotus.pipelines import *
from scotus.items import CaseLoader
from scotus.settings import TEST_DB, SCDB_TEST_FILE
from scotus.add import add_justices, add_scdb_votes

def make_case(case_file, decision_file):
  pipeline = CasePipeline()
  case_json = load_json(case_file)
  case_item = CaseLoader(case_json).load_case_data()
  decision_json = load_json(decision_file)
  decision_item = CaseLoader(decision_json, item=case_item).load_decision_data()
  return pipeline.process_item(case_item, None)

def test_case_pipeline():
  item = make_case('tests/pages/obergefell.json', 'tests/pages/obergefell_decision.json')
  assert_t(item.get('winning_party', None) == None)
  assert_t(item['winning_side']=='petitioner')
  assert_t(item['losing_side']=='respondent')

class TestPipelines():
  pipeline = OyezPipeline(db_file=TEST_DB)
  @classmethod
  def class_setup(cls):
    db = DB(TEST_DB)
    db.reset()
    build = Build()
    phase_1 = build.add(0, add_justices)
    phase_2 = build.add(1, lambda x: add_scdb_votes(x, scdb_f=SCDB_TEST_FILE), name='add_scdb_votes')
    db.populate(build)

  def setup(self):
    self.pipeline.open_session()

  def test_update_existing_case(self):
    case = make_case('tests/pages/obergefell.json', 'tests/pages/obergefell_decision.json')
    self.pipeline.process_item(case, None)
    case = self.pipeline.session.query(Case).filter(Case.docket==u"14-556").scalar()
    assert_t(len(case.questions) == 2)
    assert_t(case.oyez_id == 56149)
    assert_t(case.facts == u"Groups of same-sex couples sued their relevant state agencies in Ohio, Michigan, Kentucky, and Tennessee to challenge the constitutionality of those states\u0027 bans on same-sex marriage or refusal to recognize legal same-sex marriages that occurred in jurisdictions that provided for such marriages. The plaintiffs in each case argued that the states\u0027 statutes violated the Equal Protection Clause and Due Process Clause of the Fourteenth Amendment, and one group of plaintiffs also brought claims under the Civil Rights Act. In all the cases, the trial court found in favor of the plaintiffs. The U.S. Court of Appeals for the Sixth Circuit reversed and held that the states\u0027 bans on same-sex marriage and refusal to recognize marriages performed in other states did not violate the couples\u0027 Fourteenth Amendment rights to equal protection and due process.")

  @classmethod
  def class_teardown(cls):
    cls.pipeline.close_session()
    DB(TEST_DB).reset()
