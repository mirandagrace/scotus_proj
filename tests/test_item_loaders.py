import json
import jmespath
from datetime import date
from utilities import *
from scotus.items import CaseLoader, VoteLoader, AdvocateLoader, ArgumentLoader, SectionLoader
from scotus.items import turn_loader_factory, JusticeTurnLoader, AdvocateTurnLoader, TurnLoader


class TestItemLoaders:
  def check_load_case_data(self, testfile, item):
    case = load_json(testfile)
    loader = CaseLoader(case)
    result = dict(loader.load_case_data())
    check_arguments(item, result)

  def check_load_decision_data(self, testfile, item):
    case = load_json(testfile)
    loader = CaseLoader(case)
    result = dict(loader.load_decision_data())
    check_arguments(item, result)

  def check_load_vote_data(self, testfile, item):
    vote = load_json(testfile)
    loader = VoteLoader(vote)
    result = dict(loader.load_vote_data(56149))
    check_arguments(item, result)

  def check_load_advocate_data(self, testfile, item):
    advocate = load_json(testfile)
    loader = AdvocateLoader(advocate)
    result = dict(loader.load_advocate_data(56149))
    check_arguments(item, result)

  def check_load_argument_data(self, testfile, item):
    argument = load_json(testfile)
    loader = ArgumentLoader(argument)
    result = dict(loader.load_argument_data(56149))
    check_arguments(item, result)

  def check_load_section_data(self, testfile, item):
    section = load_json(testfile)
    loader = SectionLoader(section)
    loader.load_section_data(13186, 0)
    result = dict(loader.load_advocate_owner(19936))
    check_arguments(item, result)

  def check_load_justice_turn_data(self, testfile, item):
    turn = load_json(testfile)
    loader = turn_loader_factory(turn)
    assert loader.__class__ == JusticeTurnLoader
    result = loader.load_turn_data(13186, 0, 0)
    check_arguments(item, result)

  def check_load_advocate_turn_data(self, testfile, item):
    turn = load_json(testfile)
    loader = turn_loader_factory(turn)
    assert loader.__class__ == AdvocateTurnLoader
    result = loader.load_turn_data(13186, 0, 1)
    check_arguments(item, result)

  def check_load_unknown_turn_data(self, testfile, item):
    turn = load_json(testfile)
    loader = turn_loader_factory(turn)
    assert loader.__class__ == TurnLoader
    result = loader.load_turn_data(16189, 0, 2)
    check_arguments(item, result)

  def check_load_advocate_speaking_data(self, testfile, item):
    turn = load_json(testfile)
    loader = AdvocateLoader(turn)
    result = loader.load_speaking_data(59421)
    check_arguments(item, result)

  def test_case_loader(self):
    item_1 = {'name':"Obergefell v. Hodges",
              'granted_date': date(2015, 1, 16),
              'dec_date': date(2015, 6, 26),
              'facts': u"Groups of same-sex couples sued their relevant state agencies in Ohio, Michigan, Kentucky, and Tennessee to challenge the constitutionality of those states\u0027 bans on same-sex marriage or refusal to recognize legal same-sex marriages that occurred in jurisdictions that provided for such marriages. The plaintiffs in each case argued that the states\u0027 statutes violated the Equal Protection Clause and Due Process Clause of the Fourteenth Amendment, and one group of plaintiffs also brought claims under the Civil Rights Act. In all the cases, the trial court found in favor of the plaintiffs. The U.S. Court of Appeals for the Sixth Circuit reversed and held that the states\u0027 bans on same-sex marriage and refusal to recognize marriages performed in other states did not violate the couples\u0027 Fourteenth Amendment rights to equal protection and due process.",
              'questions': u"(1) Does the Fourteenth Amendment require a state to license a marriage between two people of the same sex?\n(2) Does the Fourteenth Amendment require a state to recognize a marriage between two people of the same sex that was legally licensed and performed in another state?",
              'conclusion': u"Yes, yes. Justice Anthony M. Kennedy delivered the opinion for the 5-4 majority. The Court held that the Due Process Clause of the Fourteenth Amendment guarantees the right to marry as one of the fundamental liberties it protects, and that analysis applies to same-sex couples in the same manner as it does to opposite-sex couples. Judicial precedent has held that the right to marry is a fundamental liberty because it is inherent to the concept of individual autonomy, it protects the most intimate association between two people, it safeguards children and families by according legal recognition to building a home and raising children, and it has historically been recognized as the keystone of social order. Because there are no differences between a same-sex union and an opposite-sex union with respect to these principles, the exclusion of same-sex couples from the right to marry violates the Due Process Clause of the Fourteenth Amendment. The Equal Protection Clause of the Fourteenth Amendment also guarantees the right of same-sex couples to marry as the denial of that right would deny same-sex couples equal protection under the law. Marriage rights have traditionally been addressed through both parts of the Fourteenth Amendment, and the same interrelated principles of liberty and equality apply with equal force to these cases; therefore, the Constitution protects the fundamental right of same-sex couples to marry. The Court also held that the First Amendment protects the rights of religious organizations to adhere to their principles, but it does not allow states to deny same-sex couples the right to marry on the same terms as those for opposite-sex couples.\nChief Justice John G. Roberts, Jr. wrote a dissent in which he argued that, while same-sex marriage might be good and fair policy, the Constitution does not address it, and therefore it is beyond the purview of the Court to decide whether states have to recognize or license such unions. Instead, this issue should be decided by individual state legislatures based on the will of their electorates. The Constitution and judicial precedent clearly protect a right to marry and require states to apply laws regarding marriage equally, but the Court cannot overstep its bounds and engage in judicial policymaking. The precedents regarding the right to marry only strike down unconstitutional limitations on marriage as it has been traditionally defined and government intrusions, and therefore there is no precedential support for making a state alter its definition of marriage. Chief Justice Roberts also argued that the majority opinion relied on an overly expansive reading of the Due Process and Equal Protection Clauses of the Fourteenth Amendment without engaging with the judicial analysis traditionally applied to such claims and while disregarding the proper role of the courts in the democratic process. Justice Antonin Scalia and Justice Clarence Thomas joined in the dissent. In his separate dissent, Justice Scalia wrote that the majority opinion overstepped the bounds of the Court\u2019s authority both by exercising the legislative, rather than judicial, power and by doing so in a realm that the Constitution reserves for the states. Justice Scalia argued that the question of whether same-sex marriage should be recognized is one for the state legislatures, and that for the issue to be decided by unelected judges goes against one of the most basic precepts of the Constitution: that political change should occur through the votes of elected representatives. In taking on this policymaking role, the majority opinion departed from established Fourteenth Amendment jurisprudence to create a right where none exists in the Constitution. Justice Thomas joined in the dissent. Justice Thomas also wrote a separate dissent in which he argued that the majority opinion stretched the doctrine of substantive due process rights found in the Fourteenth Amendment too far and in doing so distorted the democratic process by taking power from the legislature and putting it in the hands of the judiciary. Additionally, the legislative history of the Due Process Clause in both the Fifth and Fourteenth Amendments indicates that they were meant to protect people from physical restraint and from government intervention, but they do not grant them rights to government entitlements. Justice Thomas also argued that the majority opinion impermissibly infringed on religious freedom by legislating from the bench rather than allowing the state legislature to determine how best to address the competing rights and interests at stake. Justice Scalia joined in the dissent. In his separate dissent, Justice Samuel A. Alito, Jr. wrote that the Constitution does not address the right of same-sex couples to marry, and therefore the issue is reserved to the states to decide whether to depart from the traditional definition of marriage. By allowing a majority of the Court to create a new right, the majority opinion dangerously strayed from the democratic process and greatly expanded the power of the judiciary beyond what the Constitution allows. Justice Scalia and Justice Thomas joined in the dissent.",
              'docket': u"14-556",
              'oyez_id':56149,
              'petitioner':u"James Obergefell, et al.",
              'respondent':u"Richard Hodges, Director of the Ohio Department of Health, et al.",
              'volume': 576 }
    self.check_load_case_data('tests/pages/obergefell.json', item_1)

  def test_decision_loader(self):
    item_1 = {
      'dec_type': u'majority opinion',
      'prec_alt': True,
      'dec_unconst': False,
      'winning_party': u'Obergefell',
      'description': u"The Fourteenth Amendment requires both marriage licensing and recognition for same-sex couples."
    }
    self.check_load_decision_data('tests/pages/obergefell_decision.json', item_1)

  def test_vote_loader(self):
    item_1 = {
      'case_oyez_id': 56149,
      'justice_oyez_id': 15049,
      'vote': u'minority',
      'opinion_written': u'dissent',
      'opinions_joined': [15086, 15100, 15068]
    }
    self.check_load_vote_data('tests/pages/obergefell_vote_scalia.json', item_1)

  def test_advocate_loader(self):
    item_1 = {
      'case_oyez_id': 56149,
      'description': "for the petitioners on Question 1",
      'role': "amicus - us",
      'name': "Donald B. Verrilli, Jr.",
      'oyez_id': 21656
    }
    self.check_load_advocate_data('tests/pages/obergefell_advocate_verilli.json', item_1)

  def test_advocate_load_speaking(self):
    item_1 = {
      'case_oyez_id':59421,
      'name': "Charles K. Rice",
      'oyez_id': 19936
    }
    self.check_load_advocate_speaking_data('tests/pages/advocate_turn.json', item_1)

  def test_argument_loader_basic(self):
    item_1 = {
      'case_oyez_id': 56149,
      'oyez_id': 23751,
      'date': date(2015, 4, 28)
    }
    self.check_load_argument_data('tests/pages/obergefell_transcript_1.json', item_1)

  def test_section_loader(self):
    item_1 = {
      'argument_oyez_id': 13186,
      'number': 0,
      'advocate_oyez_id': 19936
    }
    self.check_load_section_data('tests/pages/oregon_section.json', item_1)

  def test_justice_turn_loader(self):
    item_1 = {
      'argument_oyez_id': 13186,
      'section_number': 0,
      'number': 0,
      'justice_oyez_id': 15089,
      'time_start': 43.911,
      'time_end': 55.349,
      'text': "You -- I suppose have put in your brief the names of those cases and the amounts involved in them substantially to the statement?"
    }
    self.check_load_justice_turn_data('tests/pages/justice_turn.json', item_1)

  def test_advocate_turn_loader(self):
    item_1 = {
      'argument_oyez_id': 13186,
      'section_number': 0,
      'number': 1,
      'advocate_oyez_id': 19936,
      'time_start': 0,
      'time_end': 43.911,
      'text': u"I\u0027m including my remarks with respect to the (Inaudible) the application of 3616. I think it is fair to say that the purposes applying that particular section were to -- to meet the protest of the District Courts, the various District Courts and the United States Attorneys in the various districts. And to ameliorate a lot of the small taxpayer who was being subjected to a felony prosecution and summonses where the tax involved was as low as a $100 or a $150."
    }
    self.check_load_advocate_turn_data('tests/pages/advocate_turn.json', item_1)

  def test_unknown_turn_loader(self):
    item_1 = {
      'argument_oyez_id': 16189,
      'section_number': 0,
      'number': 2,
      'time_start': 886.611,
      'time_end': 892.361,
      'text': "Well, we reserved it only one way, in one direction?"
    }
    self.check_load_unknown_turn_data('tests/pages/unknown_turn.json', item_1)

  def test_turn_loader_factory_unknown(self):
    unknown_json = load_json('tests/pages/unknown_turn.json')
    loader=turn_loader_factory(unknown_json)
    assert_eq(loader.__class__, TurnLoader)

  def test_turn_loader_factory_advocate(self):
    advocate_json = load_json('tests/pages/advocate_turn.json')
    loader=turn_loader_factory(advocate_json)
    assert_eq(loader.__class__, AdvocateTurnLoader)

  def test_turn_loader_factory_justice(self):
    advocate_json = load_json('tests/pages/justice_turn.json')
    loader=turn_loader_factory(advocate_json)
    assert_eq(loader.__class__, JusticeTurnLoader)



  