#!/usr/bin/env python
# -*- coding: utf-8 -*-
from StringIO import StringIO
import csv

def make_dict(s):
  csvfile = StringIO(s)
  reader = csv.DictReader(csvfile, fieldnames=HEADERS)
  for cr in reader:
    return cr


HEADERS = ["caseId","docketId","caseIssuesId","voteId","dateDecision","decisionType","usCite","sctCite","ledCite","lexisCite","term","naturalCourt","chief","docket","caseName","dateArgument","dateRearg","petitioner","petitionerState","respondent","respondentState","jurisdiction","adminAction","adminActionState","threeJudgeFdc","caseOrigin","caseOriginState","caseSource","caseSourceState","lcDisagreement","certReason","lcDisposition","lcDispositionDirection","declarationUncon","caseDisposition","caseDispositionUnusual","partyWinning","precedentAlteration","voteUnclear","issue","issueArea","decisionDirection","decisionDirectionDissent","authorityDecision1","authorityDecision2","lawType","lawSupp","lawMinor","majOpinWriter","majOpinAssigner","splitVote","majVotes","minVotes","justice","justiceName","vote","opinion","direction","majority","firstAgreement","secondAgreement"]

test_strings = ['"1946-001","1946-001-01","1946-001-01-01","1946-001-01-01-01-01",11/18/1946,1,"329 U.S. 1","67 S. Ct. 6","91 L. Ed. 3","1946 U.S. LEXIS 1724",1946,1301,"Vinson","24","HALLIBURTON OIL WELL CEMENTING CO. v. WALKER et al., DOING BUSINESS AS DEPTHOGRAPH CO.",1/9/1946,10/23/1946,198,,172,,6,,,0,51,6,29,,0,11,2,1,1,3,0,1,1,0,80180,8,2,0,4,,6,600,"35 U.S.C. § 33",78,78,1,8,1,86,"HHBurton",2,1,1,1,,\n'
,
                '"2014-040","2014-040-01","2014-040-01-01","2014-040-01-01-01-01",6/25/2015,1,,,,"2015 U.S. LEXIS 4249",2014,1704,"Roberts","13-1371","TEXAS DEPARTMENT OF HOUSING AND COMMUNITY AFFAIRS v. INCLUSIVE COMMUNITIES PROJECT, INC.",1/21/2015,,7,51,192,,1,,,0,120,,25,,0,11,4,2,1,2,0,0,0,0,20040,2,2,0,4,,3,342,"NA",106,106,1,5,4,111,"JGRoberts",2,1,1,1,112,\n']
