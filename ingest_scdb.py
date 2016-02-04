#!/usr/bin/env python
# -*- coding: utf-8 -*-
import csv
import re
from datetime import date
from db import *
from scdb_labels import *

SCDB_ISSUE_FILE = 'data/scdb/SCDB_2015_01_caseCentered_LegalProvision.csv'
SCDB_CASE_FILE = 'data/scdb/SCDB_2015_01_caseCentered_Citation.csv'
SCDB_VOTE_FILE = 'data/scdb/SCDB_2015_01_justiceCentered_Citation.csv'

def add_case(case_row, session):
  # make and add case
  case = Case(**parse_case(case_row))
  session.add(case)
  session.commit()
  # make and add parties
  petitioner, respondent = parse_parties(case_row)
  case.petitioner = Petitioner(**petitioner)
  case.respondent = Respondent(**respondent)
  session.commit()
  return case
  
# add all the 
def add_cases(session, num=-1):
  # open the csv file
  with open(SCDB_CASE_FILE, 'r') as csvfile:
    reader = csv.DictReader(csvfile)
    count = 0
    # iterate through the cases, adding as you go
    for case_row in reader:
      add_case(case_row, session)
      count += 1
      if count == num:
        break    
  return
 
# make the justices table
def add_justices(session):
  for name in set(justice_names):
    justice = Justice(**{'name':name})
    session.add(justice)
    session.commit()
  return
  
def add_vote(vote_row, case_id, justice_id, session):
  vote = Vote(parse_vote(vote_row, case_id, justice_id))
  session.add(vote)
  session.commit()
  return vote
  
  
def add_votes(session, num=-1):
  justice_dict = Justice.by_name(session)
  with open(SCDB_VOTE_FILE, 'r') as csvfile:
    reader = csv.DictReader(csvfile)
    count = 0
    case = None
    # iterate through the votes, adding as you go
    for vote_row in reader:
      # if we need to, make a new case.
      if case == None or current_case.scdb_id != vote_row['caseId']:
        case = add_case(vote_row, session)
        count += 1
        if count == num:
          return
      case_id = case.id
      justice_id = justice_dict[(parse_justice_name(vote_row['justice']))]
      add_vote(vote_row, case_id, justice_id, session)    
  
# function for applying the same function to transform multiple keys from a row_dict
# to arguments for a sqlalchemy constructor.  
def batch_process(dict, keys, function):
  return {out_k:function(dict[in_k]) for in_k, out_k in keys}

def process_string(s):
  if len(s)>0:
    return s.decode('utf-8')
  else:
    return None
  
# given a case dictionary from the scdb csv, return a dictionary of the arguments to the
# Case constructor
def parse_case(case_row):
  case = {}
  # string variables -- Variables that are strings and already in the form needed
  str_vars = [('caseId', 'scdb_id'), ('usCite', 'citation'), ('docket', 'docket'),
              ('caseName', 'name')]
  case.update(batch_process(case_row, str_vars, process_string))
  # date variable
  month, day, year = case_row['dateDecision'].split('/')
  case['dec_date'] = date(int(year), int(month), int(day))
  # boolean variables
  if case_row['declarationUncon'] != None:
    case['dec_unconst'] = case_row['declarationUncon']!='1'
  else:
    pass
  if case_row['precedentAlteration'] != None:
    case['prec_alt'] = case_row['precedentAlteration']=='1'
  else:
    pass
  # labeled text variables
  case['jurisdiction'] = parse_jurisdiction(case_row['jurisdiction'])
  case['cert_reason'] = parse_cert(case_row['certReason'])
  case['admin'] = parse_admin_agency(case_row['adminAction'])
  case['admin_loc'] = parse_state(case_row['adminActionState'])
  case['origin'] = parse_court(case_row['caseOrigin'])
  case['orig_loc'] = parse_state(case_row['caseOriginState'])
  case['lower_court'] = parse_court(case_row['caseSource'])
  case['low_court_loc'] = parse_state(case_row['caseSourceState'])
  case['low_court_disp'] = parse_lc_disposition(case_row['lcDisposition'])
  case['low_court_disp_dir'] = parse_direction(case_row['lcDispositionDirection'])
  case['disposition'] = parse_sc_disposition(case_row['caseDisposition'])
  case['dec_dir'] = parse_direction(case_row['decisionDirection'])
  case['dec_type'] = parse_decision_kind(case_row['decisionType'])
  if case['dec_type'] == None:
    case['per_curiam'] = None
  else:
    case['per_curiam'] = (case_row['decisionType'] == '2' or case_row['decisionType'] == '6')
  if case_row['partyWinning'] == '1':
    case['winning_side'] = u'petitioner'
  elif case_row['partyWinning'] == '0':
    case['winning_side'] = u'respondent'
  return case
  
def parse_labels(labels, null=None, d=False):
  def parse(x):
    if x == null or x=='' or x == None :
      return None
    elif d:
      return labels[x]
    else:
      return labels[int(x)-1]
  return parse
    
parse_jurisdiction = lambda x: parse_labels(jurisdiction_labels, null='15')(x)
parse_admin_agency = lambda x: parse_labels(admin_agency_labels, null='118')(x)
parse_state = lambda x: parse_labels(state_labels)(x)
parse_court = lambda x: parse_labels(court_labels, d=True)(x)
parse_cert = lambda x: parse_labels(cert_labels, null='12')(x)
parse_lc_disposition = lambda x: parse_labels(lc_disposition_labels)(x)
parse_sc_disposition = lambda x: parse_labels(sc_disposition_labels)(x)
parse_direction = lambda x: parse_labels(direction_labels, null='3')(x)
parse_decision_kind = lambda x: parse_labels(decision_kind)(x)
parse_party = lambda x: parse_labels(party_codes, d=True)(x)
parse_justice_name = lambda x: parse_labels(justice_names)(x)
parse_vote_kind = lambda x: parse_labels(vote_labels)(x)

def parse_parties(case_row):
  try:
    petitioner_name, respondant_name = re.split(r' v[.] ', case_row['caseName'].decode('utf-8'), 1)
    petitioner = {'name' : petitioner_name, 'side':'petitioner'}
    respondent = {'name' : respondant_name, 'side':'respondent'}
  except:
    petitioner = {}
    respondent = {}
  petitioner['kind'] = parse_party(case_row['petitioner'])
  petitioner['location'] = parse_state(case_row['petitionerState'])
  respondent['kind'] = parse_party(case_row['respondent'])
  respondent['location'] = parse_state(case_row['respondentState'])
  # if case_row['partyWinning'] == '1':
    # petitioner['winner'] = True
    # respondent['winner'] = False
  # elif case_row['partyWinning'] == '0':
    # petitioner['winner'] = False
    # respondent['winner'] = True
  return petitioner, respondent
  
def parse_vote(vote_row, case_id, justice_id):
  vote = {'justice_id': justice_id, 'case_id':case_id}
  vote['is_clear'] = vote_row['voteUnclear'] == '0'
  vote['with_majority'] = vote_row['majority'] == '2'
  vote['direction'] = vote_row['direction']
  vote['kind'] = parse_vote_kind(vote_row['vote'])
  return vote

# main function that builds the database
def ingest_scdb(num=-1):
  session = Session()
  # start with the reading in just the case data
  #add_cases(session, num=num)
  add_justices(session)
  add_votes(session, num)
  # TODO: add vote data
  # TODO: add issue tagging 
  return
        
if __name__ == "__main__":
    ingest_scdb()