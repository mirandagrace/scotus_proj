# -*- coding: utf-8 -*-
from ..scdb.parse import *
from utilities import *

def check_arguments(d, expected_d):
  for k in expected_d:
    assert_in(k, d)
  for k in d:
    assert_in(k, expected_d)
    assert_eq(d[k], expected_d[k])
  return  

def test_parse_case():
  for e, s in zip(expected_cases, test_strings):
    case = parse_case(make_dict(s))
    yield check_arguments, case, e
    
def test_parse_male_justice():
  check_arguments(parse_justice('John G. Roberts, Jr.'), {'name': 'John G. Roberts, Jr.', 'gender':'M'})
  
def test_parse_female_justice():
  check_arguments(parse_justice('Elena Kagan'), {'name': 'Elena Kagan', 'gender':'F'})

def test_parse_parties():
  parties = map(lambda x: parse_parties(make_dict(x)), test_strings)
  petitioners = map(lambda x: x[0], parties)
  respondents = map(lambda x: x[1], parties)
  for p, petitioner in zip(expected_petitioners, petitioners):
    yield check_arguments, p, petitioner
  for r, respondent in zip(expected_respondents, respondents):
    yield check_arguments, r, respondent
    
def test_parse_vote():
  id = 1
  for e, s in zip(expected_votes, test_strings):
    vote = parse_vote(make_dict(s), id)
    yield check_arguments, vote, e
    id += 1