#!/usr/bin/env python
# -*- coding: utf-8 -*-
# parses the data from 
import csv
import re
from datetime import date
from labels import *

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
  
def parse_justice(name):
    if name in female_justices:
      gender = u'F'
    else:
      gender = u'M'
    return {'name': name.decode('utf-8'), 'gender':gender}
  
def parse_labels(labels, null=None, d=False):
  def parse(x):
    if x == null or x=='' or x == None :
      return None
    elif d:
      return labels[x]
    else:
      return labels[int(x)-1]
  return parse
    
parse_jurisdiction = parse_labels(jurisdiction_labels, null='15')
parse_admin_agency = parse_labels(admin_agency_labels, null='118')
parse_state = parse_labels(state_labels)
parse_court = parse_labels(court_labels, d=True)
parse_cert = parse_labels(cert_labels, null='12')
parse_lc_disposition = parse_labels(lc_disposition_labels)
parse_sc_disposition = parse_labels(sc_disposition_labels, null='11')
parse_direction = parse_labels(direction_labels, null='3')
parse_decision_kind =  parse_labels(decision_kind)
parse_party = parse_labels(party_codes, d=True, null='501')
parse_justice_name = parse_labels(justice_names)
parse_vote_kind = parse_labels(vote_labels)

def parse_parties(case_row):
  try:
    petitioner_name, respondant_name = re.split(r' v[.] ', case_row['caseName'].decode('utf-8'), 1)
    petitioner = {'name' : petitioner_name, 'side':'petitioner'}
    respondent = {'name' : respondant_name, 'side':'respondent'}
  except:
    petitioner = {'name' : None, 'side':'petitioner'}
    respondent = {'name' : None, 'side':'respondent'}
  petitioner['kind'] = parse_party(case_row['petitioner'])
  petitioner['location'] = parse_state(case_row['petitionerState'])
  respondent['kind'] = parse_party(case_row['respondent'])
  respondent['location'] = parse_state(case_row['respondentState'])
  if case_row['partyWinning'] == '1':
    petitioner['winner'] = True
    respondent['winner'] = False
  elif case_row['partyWinning'] == '0':
    petitioner['winner'] = False
    respondent['winner'] = True
  return petitioner, respondent
  
def parse_vote(vote_row, case_id, justice_id):
  vote = {'justice_id': justice_id, 'case_id':case_id}
  vote['is_clear'] = vote_row['voteUnclear'] == '0'
  vote['with_majority'] = vote_row['majority'] == '2'
  vote['direction'] =  parse_direction(vote_row['direction'])
  vote['kind'] = parse_vote_kind(vote_row['vote'])
  return vote
