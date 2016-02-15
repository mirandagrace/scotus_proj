# -*- coding: utf-8 -*-
import csv
import json
from StringIO import StringIO
from datetime import date
from scotus.config import TEST_DB, SCDB_TEST_FILE


def load_json(filename):
  with open(testfile, 'rb') as f:
    json_object = json.load(f) 
  return json_object

def make_dict(s):
  csvfile = StringIO(s)
  reader = csv.DictReader(csvfile, 
                          fieldnames=["caseId","docketId","caseIssuesId","voteId","dateDecision","decisionType","usCite","sctCite","ledCite","lexisCite","term","naturalCourt","chief","docket","caseName","dateArgument","dateRearg","petitioner","petitionerState","respondent","respondentState","jurisdiction","adminAction","adminActionState","threeJudgeFdc","caseOrigin","caseOriginState","caseSource","caseSourceState","lcDisagreement","certReason","lcDisposition","lcDispositionDirection","declarationUncon","caseDisposition","caseDispositionUnusual","partyWinning","precedentAlteration","voteUnclear","issue","issueArea","decisionDirection","decisionDirectionDissent","authorityDecision1","authorityDecision2","lawType","lawSupp","lawMinor","majOpinWriter","majOpinAssigner","splitVote","majVotes","minVotes","justice","justiceName","vote","opinion","direction","majority","firstAgreement","secondAgreement"])
  for cr in reader:
    return cr

def assert_in(k, d):
  assert k in d, 'key missing: {}'.format(k)

def assert_eq(d1, d2):
  assert d1 == d2, 'equality fail: got "{}" and expected "{}"'.format(d1, d2)

def assert_t(d):
  assert d

def assert_f(d):
  assert not d

def raises(fn, e):
  try:
    fn()
  except e:
    return True 
  return False

  
def check_arguments(d, expected_d):
  for k in expected_d:
    assert_in(k, d)
  for k in d:
    assert_in(k, expected_d)
    assert_eq(d[k], expected_d[k])
  return 
