#!/usr/bin/env python
# -*- coding: utf-8 -*-
import csv
from datetime import date
from scotus_proj import Session
from models import Case
from scdb_labels import *

SCDB_ISSUE_FILE = 'data/scdb/SCDB_2015_01_caseCentered_LegalProvision.csv'
SCDB_CASE_FILE = 'data/scdb/SCDB_2015_01_caseCentered_Citation.csv'
SCDB_VOTE_FILE = 'data/scdb/SCDB_2015_01_justiceCentered_Citation.csv'

def add_case(case_row, session):
  case_data = Case(parse_case(case_row))
  # TODO: Process case, send to database.
  return  
  
# add all the 
def add_cases(session):
  # open the csv file
  with open(SCDB_CASE_FILE, 'r') as csvfile:
    reader = csv.DictReader(csvfile)
    # iterate through the cases, adding as you go
    for case_row in read:
      add_case(case_row, session)
  return
  
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
  case['dec_unconst'] = case_row['declarationUncon']!='1'
  case['prec_alt'] = case_row['precedentAlteration']=='1'
  # labeled text variables
  case['jurisdiction'] = parse_jurisdiction(case_row['jurisdiction'])
  case['cert_reason'] = parse_cert(case_row['certReason'])
  case['admin'] = parse_admin_agency(case_row['adminAction'])
  case['admin_loc'] = parse_state(case_row['adminActionState'])
  case['origin'] = parse_court(case_row['caseOrigin'])
  case['orig_loc'] = parse_state(case_row['caseOriginState'])
  case['lower_court'] = parse_court(case_row['caseSource'])
  case['low_court_loc'] = parse_state(case_row['caseSourceState'])
  case['low_court_disp'] = parse_disposition(case_row['lcDisposition'])
  case['low_court_disp_dir'] = parse_direction(case_row['lcDispositionDirection'])
  case['dec_dir'] = parse_direction(case_row['decisionDirection'])
  case['dec_type'] = parse_decision_kind(case_row['decisionType'])
  if case['dec_type'] == None:
    case['per_curiam'] = None
  else:
    case['per_curiam'] = (case_row['decisionType'] == '2' or case_row['decisionType'] == '6') 
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
parse_disposition = lambda x: parse_labels(disposition_labels)(x)
parse_direction = lambda x: parse_labels(direction_labels, null='3')(x)
parse_decision_kind = lambda x: parse_labels(decision_kind)(x)

# main function that builds the database
def main():
  session = Session()
  # start with the reading in just the case data
  add_cases(session)
  # TODO: add vote data
  # TODO: add issue tagging 
  return
        
if __name__ == "__main__":
    main()