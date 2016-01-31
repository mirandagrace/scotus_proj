import csv
import StringIO
import datetime

CASE_HEADERS = ["caseId","docketId","caseIssuesId","voteId","dateDecision","decisionType","usCite","sctCite","ledCite","lexisCite","term","naturalCourt","chief","docket","caseName","dateArgument","dateRearg","petitioner","petitionerState","respondent","respondentState","jurisdiction","adminAction","adminActionState","threeJudgeFdc","caseOrigin","caseOriginState","caseSource","caseSourceState","lcDisagreement","certReason","lcDisposition","lcDispositionDirection","declarationUncon","caseDisposition","caseDispositionUnusual","partyWinning","precedentAlteration","voteUnclear","issue","issueArea","decisionDirection","decisionDirectionDissent","authorityDecision1","authorityDecision2","lawType","lawSupp","lawMinor","majOpinWriter","majOpinAssigner","splitVote","majVotes","minVotes"]

def make_case(s):
  with StringIO(s) as csvfile:
    reader = csv.DictReader(csvfile, headers=CASE_HEADERS)
    for cr in reader:
      case_row = cr
      break
  return cr

def test_process_case():
  test_string = '"1946-001","1946-001-01","1946-001-01-01","1946-001-01-01-01",11/18/1946,1,"329 U.S. 1","67 S. Ct. 6","91 L. Ed. 3","1946 U.S. LEXIS 1724",1946,1301,"Vinson","24","HALLIBURTON OIL WELL CEMENTING CO. v. WALKER et al., DOING BUSINESS AS DEPTHOGRAPH CO.",1/9/1946,10/23/1946,198,,172,,6,,,0,51,6,29,,0,11,2,1,1,3,0,1,1,0,80180,8,2,0,4,,6,600,"35 U.S.C. § 33",78,78,1,8,1\n'
  case = make_case(test_string)
  expected_case = {'scdb_id': "1946-001",
                   'citation': "329 U.S. 1",
                   'docket': "24",
                   'name': "HALLIBURTON OIL WELL CEMENTING CO. v. WALKER et al., DOING BUSINESS AS DEPTHOGRAPH CO."
                   'juristiction': "rehearing or restored to calendar for reargument"
                   'cert_reason': 
                   'admin': None
                   'admin_loc': None
                   'origin': "California Southern U.S. District Court"
                   'orig_loc': "California"
                   'lower_court': "U.S. Court of Appeals, Ninth Circuit"
                   'low_court_loc': None
                   'low_court_disp': "affirmed"
                   'low_court_disp_dir': "conservative"
                   'dec_date': date(1946, 18, 11),
                  # 'granted_date':
                   'dec_dir': "liberal"
                   'dec_type': "opinion of the court (orally argued)"
                   'dec_unconst': False
                   'prec_alt': True
                   'per_curiam':False}
                   #'syllabus': 
                   #'holding':
                   #'facts':
                   #'conclusion':}

  for k in expected_case:
    assert case[k] == expected_case[k]
  assert case == expected_case
  return