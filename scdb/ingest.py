#!/usr/bin/env python
# -*- coding: utf-8 -*-
import csv
import re
from datetime import date
from ..config import SCDB_VOTES_FILE
from labels import justice_names
from parse import *
from ..models import Case, Justice, Petitioner, Respondent, Vote

def add_case(case_row, session):
  # make and add case
  case = Case(**parse_case(case_row))
  session.add(case)
  # make and add parties
  petitioner, respondent = parse_parties(case_row)
  case.petitioner = Petitioner(**petitioner)
  case.respondent = Respondent(**respondent)
  return case
 
# make the justices table
def add_justices(session):
  for name in set(justice_names):
    justice = Justice(**parse_justice(name))
    session.add(justice)
  return
  
def add_vote(vote_row, case_id, justice_id, session):
  vote = Vote(parse_vote(vote_row, case_id, justice_id))
  session.add(vote)
  return vote
  
def add_votes(session, file=SCDB_VOTES_FILE):
  justice_dict = Justice.by_name(session)
  with open(SCDB_VOTES_FILE, 'r') as csvfile:
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
  
# main function that builds the database
def ingest(session):
  # start with the reading in just the case data
  #add_cases(session, num=num)
  add_justices(session)
  add_votes(session)
  # TODO: add issue tagging 
  return