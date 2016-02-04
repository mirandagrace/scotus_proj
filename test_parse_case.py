#!/usr/bin/env python
# -*- coding: utf-8 -*-
import csv
from StringIO import StringIO
from datetime import date
from scdb_labels import court_labels
from ingest_scdb import *

CASE_HEADERS = ["caseId","docketId","caseIssuesId","voteId","dateDecision","decisionType","usCite","sctCite","ledCite","lexisCite","term","naturalCourt","chief","docket","caseName","dateArgument","dateRearg","petitioner","petitionerState","respondent","respondentState","jurisdiction","adminAction","adminActionState","threeJudgeFdc","caseOrigin","caseOriginState","caseSource","caseSourceState","lcDisagreement","certReason","lcDisposition","lcDispositionDirection","declarationUncon","caseDisposition","caseDispositionUnusual","partyWinning","precedentAlteration","voteUnclear","issue","issueArea","decisionDirection","decisionDirectionDissent","authorityDecision1","authorityDecision2","lawType","lawSupp","lawMinor","majOpinWriter","majOpinAssigner","splitVote","majVotes","minVotes"]

def make_case(s):
  csvfile = StringIO(s)
  reader = csv.DictReader(csvfile, fieldnames=CASE_HEADERS)
  for cr in reader:
    case_row = cr
    break
  return cr

def assert_in(k, d):
  assert k in d, 'key missing: {}'.format(k)

def assert_equal(k, d1, d2):
  assert d1[k] == d2[k], 'key equality fail: {}, got "{}" and expected "{}"'.format(k, d1[k], d2[k])

def check_arguments(d, expected_d):
  for k in expected_d:
    assert_in(k, d)
  for k in d:
    assert_in(k, expected_d)
    assert_equal(k, d, expected_d)
  return  

def check_parse_case(test_string, expected_case):
  case = parse_case(make_case(test_string))
  yield check_arguments(case, expected_case)
  return

def check_parse_parties(test_string, expected_petitioner, expected_respondent):
  petitioner, respondent = parse_parties(test_string)
  yield check_arguments(petitioner, expected_petitioner)
  yield check_arguments(respondent, expected_respondent)

c1 = {'scdb_id': "1946-001",
      'citation': "329 U.S. 1",
      'docket': "24",
      'name': "HALLIBURTON OIL WELL CEMENTING CO. v. WALKER et al., DOING BUSINESS AS DEPTHOGRAPH CO.",
      'jurisdiction': "rehearing or restored to calendar for reargument",
      'cert_reason': 'to resolve question presented',
      'admin': None,
      'admin_loc': None,
      'origin': "California Southern U.S. District Court",
      'orig_loc': "California",
      'lower_court': "U.S. Court of Appeals, Ninth Circuit",
      'low_court_loc': None,
      'low_court_disp': "affirmed",
      'low_court_disp_dir': "conservative",
      'dec_date': date(1946, 11, 18),
    # 'granted_date':
      'dec_dir': "liberal",
      'dec_type': "opinion of the court (orally argued)",
      'disposition':'reversed',
      'dec_unconst': False,
      'prec_alt': True,
      'per_curiam':False,
      'winning_side':'petitioner'}
      #'syllabus': 
      #'holding':
      #'facts':
      #'conclusion':}

c2 = {'scdb_id': "2014-040",
      'citation': None,
      'docket': "13-1371",
      'name': "TEXAS DEPARTMENT OF HOUSING AND COMMUNITY AFFAIRS v. INCLUSIVE COMMUNITIES PROJECT, INC.",
      'jurisdiction': "cert",
      'cert_reason': 'to resolve question presented',
      'admin':  'General Land Office or Commissioners',
      'admin_loc': None,
      'origin': "Texas Northern U.S. District Court",
      'orig_loc': None,
      'lower_court': "U.S. Court of Appeals, Fifth Circuit",
      'low_court_loc': None,
      'low_court_disp': "reversed and remanded",
      'low_court_disp_dir': "liberal",
      'dec_date': date(2015,6, 25),
    # 'granted_date':
      'dec_dir': "liberal",
      'dec_type': "opinion of the court (orally argued)",
      'dec_unconst': False,
      'prec_alt': False,
      'per_curiam':False,
      'winning_side':'respondent',
      'disposition': 'affirmed (includes modified)'}
      #'syllabus': 
      #'holding':
      #'facts':
      #'conclusion':}

p1 = {'name': 'HALLIBURTON OIL WELL CEMENTING CO. v. WALKER et al.',
      'kind': 'oil company, or natural gas producer',
      'side': 'petitioner'}
r1 = {'name': 'WALKER et al., DOING BUSINESS AS DEPTHOGRAPH CO.',
      'kind': 'inventor, patent assigner, trademark owner or holder',
      'side': 'respondent'}
p2 = {'name': 'TEXAS DEPARTMENT OF HOUSING AND COMMUNITY AFFAIRS',
      'kind': 'state department or agency',
      'location': 'Texas',
      'side': 'petitioner'}
r2 = {'name': 'INCLUSIVE COMMUNITIES PROJECT, INC.',
      'kind': 'inonprofit organization or business',
      'side': 'respondent'}

expected_cases = [c1, c2]
expected_petitioners = [p1]
expected_respondents = [r1]
test_strings = ['"1946-001","1946-001-01","1946-001-01-01","1946-001-01-01-01",11/18/1946,1,"329 U.S. 1","67 S. Ct. 6","91 L. Ed. 3","1946 U.S. LEXIS 1724",1946,1301,"Vinson","24","HALLIBURTON OIL WELL CEMENTING CO. v. WALKER et al., DOING BUSINESS AS DEPTHOGRAPH CO.",1/9/1946,10/23/1946,198,,172,,6,,,0,51,6,29,,0,11,2,1,1,3,0,1,1,0,80180,8,2,0,4,,6,600,"35 U.S.C. § 33",78,78,1,8,1\n',
                '"2014-040","2014-040-01","2014-040-01-01","2014-040-01-01-01",6/25/2015,1,,,,"2015 U.S. LEXIS 4249",2014,1704,"Roberts","13-1371","TEXAS DEPARTMENT OF HOUSING AND COMMUNITY AFFAIRS v. INCLUSIVE COMMUNITIES PROJECT, INC.",1/21/2015,,7,51,192,,1,123,,0,120,,25,,0,11,4,2,1,2,0,0,0,0,20040,2,2,0,4,,3,342,"NA",106,106,1,5,4\n']
def test_parse_case():
  for e, s in zip(expected_cases, test_strings):
    yield check_parse_case, s, e

def test_parse_parties():
  for p, r, c in zip(expected_petitioners, expected_respondents, test_strings):
    yield check_parse_parties, p, r, c




