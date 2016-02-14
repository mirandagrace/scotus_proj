from scotus.oyez.items import CaseLoader
import json
from datetime import date
from scrapy.http import Response
from utilities import *

class TestItemLoaders:
  def check_load_case_data(self, testfile, item):
    with open(testfile, 'rb') as f:
      case = json.load(f) 
    loader = CaseLoader(case)
    result = dict(loader.load_case_data())
    check_arguments(item, result)

  def check_load_decision_data(self, testfile, item):
    with open(testfile, 'rb') as f:
      case = json.load(f) 
    loader = CaseLoader(case)
    result = dict(loader.load_decision_data())
    check_arguments(item, result)

  def test_case_loader_basic(self):
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

  def test_decision_loader_basic(self):
    item_1 = {
      'dec_type': u'majority opinion',
      'prec_alt': True,
      'dec_unconst': False,
      'winning_party': u'Obergefell',
      'description': u"The Fourteenth Amendment requires both marriage licensing and recognition for same-sex couples."
    }
    self.check_load_decision_data('tests/pages/obergefell_decision.json', item_1)

  