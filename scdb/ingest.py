#!/usr/bin/env python
# -*- coding: utf-8 -*-
import csv
import re
from datetime import date
from time import time
from ..config import SCDB_VOTES_FILE, SCDB_HEADERS
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
  
def add_votes(session, f, print_progress=False):
  justice_dict = Justice.by_name(session)
  with open(f, 'r') as csvfile:
    reader = csv.DictReader(csvfile, fieldnames=SCDB_HEADERS)
    count = 0
    t0 = time()
    case = None
    # iterate through the votes, adding as you go
    for vote_row in reader:
      # if we need to, make a new case.
      if case == None or case.scdb_id != vote_row['caseId']:
        case = add_case(vote_row, session)
      justice_id = justice_dict[parse_justice_name(vote_row['justice'])]
      case.votes.append(Vote(**parse_vote(vote_row, justice_id)))
      count += 1
      if count % 1000 == 0 and print_progress: # pragma: no cover
        print "Added {} votes in {} seconds".format(count, time()-t0)
  return  
  
# main function that builds the database
def ingest(session, f=SCDB_VOTES_FILE):
  add_justices(session)
  add_votes(session, f)
  # TODO: add issue tagging 
  return