import json
from datetime import date
from ..config import JUSTICES_FILE, SCDB_VOTES_FILE
from ..parse import *
from .models import Case, Justice, Petitioner, Respondent, Vote
from ..scdb_labels import justice_names, female_justices
  
def add_justices(session, j_file=JUSTICES_FILE):
  added = []
  with open(j_file, 'r') as justices_json:
    justices = json.load(justices_json)
  for justice in justices:
    jd = parse_justice(justice)
    session.add(Justice(**jd))
    added.append(jd['name'])
  for justice in justice_names:
    if justice not in added:
      if jd['name'] in female_justices:
        gender = u'F'
      else:
        gender = u'M'
      session.add(Justice(name=justice.decode('utf-8'), gender=gender))
      added.append(justice)
  return

def add_scdb_case(case_row, session):
  # make and add case
  case = Case(**parse_case(case_row))
  session.add(case)
  # make and add parties
  petitioner, respondent = parse_parties(case_row)
  case.petitioner = Petitioner(**petitioner)
  case.respondent = Respondent(**respondent)
  return case
  
def add_scdb_votes(session, scdb_f=SCDB_VOTES_FILE):
  justice_dict = Justice.by_name(session)
  with open(scdb_f, 'r') as csvfile:
    reader = csv.DictReader(csvfile)
    case = None
    # iterate through the votes, adding as you go
    for vote_row in reader:
      # if we need to, make a new case.
      if case == None or case.scdb_id != vote_row['caseId']:
        case = add_scdb_case(vote_row, session)
      justice_id = justice_dict[parse_justice_name(vote_row['justice'])]
      case.votes.append(Vote(**parse_vote(vote_row, justice_id)))
  return