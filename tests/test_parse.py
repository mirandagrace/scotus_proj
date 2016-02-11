# -*- coding: utf-8 -*-
from scotus.parse import *
from scotus.scdb_labels import female_justices
from utilities import *

class TestParse():
  test_strings = ['"1946-001","1946-001-01","1946-001-01-01","1946-001-01-01-01-01",11/18/1946,1,"329 U.S. 1","67 S. Ct. 6","91 L. Ed. 3","1946 U.S. LEXIS 1724",1946,1301,"Vinson","24","HALLIBURTON OIL WELL CEMENTING CO. v. WALKER et al., DOING BUSINESS AS DEPTHOGRAPH CO.",1/9/1946,10/23/1946,198,,172,,6,,,0,51,6,29,,0,11,2,1,1,3,0,1,1,0,80180,8,2,0,4,,6,600,"35 U.S.C. ยง 33",78,78,1,8,1,86,"HHBurton",2,1,1,1,,\n'
,
                '"2014-040","2014-040-01","2014-040-01-01","2014-040-01-01-01-01",6/25/2015,1,,,,"2015 U.S. LEXIS 4249",2014,1704,"Roberts","13-1371","TEXAS DEPARTMENT OF HOUSING AND COMMUNITY AFFAIRS v. INCLUSIVE COMMUNITIES PROJECT, INC.",1/21/2015,,7,51,192,,1,,,0,120,,25,,0,11,4,2,1,2,0,0,0,0,20040,2,2,0,4,,3,342,"NA",106,106,1,5,4,111,"JGRoberts",2,1,1,1,112,\n']

  c1 = {'scdb_id': "1946-001",
        'citation': Citation(329, 1),
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
        'dec_type': "majority opinion",
        'disposition':'reversed',
        'dec_unconst': False,
        'prec_alt': True,
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
        'admin':  None,
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
        'dec_type': "majority opinion",
        'dec_unconst': False,
        'prec_alt': False,
        'winning_side':'respondent',
        'disposition': 'affirmed (includes modified)'}
        #'syllabus': 
        #'holding':
        #'facts':
        #'conclusion':}

  p1 = {'name': 'HALLIBURTON OIL WELL CEMENTING CO.',
        'kind': 'oil company, or natural gas producer',
        'side': 'petitioner',
        'location': None,
        'winner': True}
  r1 = {'name': 'WALKER et al., DOING BUSINESS AS DEPTHOGRAPH CO.',
        'kind': 'inventor, patent assigner, trademark owner or holder',
        'side': 'respondent',
        'location': None,
        'winner': False}
  p2 = {'name': 'TEXAS DEPARTMENT OF HOUSING AND COMMUNITY AFFAIRS',
        'kind': 'state department or agency',
        'location': 'Texas',
        'side': 'petitioner',
        'winner': False}
  r2 = {'name': 'INCLUSIVE COMMUNITIES PROJECT, INC.',
        'kind': 'nonprofit organization or business',
        'location': None,
        'side': 'respondent',
        'winner': True}
        
  v1 = {'justice_id' : 1,
         'is_clear' : True,
         'vote' : 'minority',
         #'kind' : 'dissent',
         'direction' : 'conservative'}
         
  v2 = { 'justice_id' : 2,
         'is_clear' : True,
         'vote' : 'minority',
         #'kind' : 'dissent',
         'direction' : 'conservative'}
         
  j1 = {"ID":15094,"name":"Elena Kagan","href":"https:\/\/api.oyez.org\/people\/elena_kagan","last_name":"Kagan","roles":[{"id":2738,"type":"scotus_justice","date_start":1281157200,"date_end":0,"appointing_president":"Barack Obama","role_title":"Associate Justice of the Supreme Court of the United States","institution_name":"Supreme Court of the United States","href":"https:\/\/api.oyez.org\/preson_role\/scotus_justice\/2738"}],"thumbnail":{"id":32690,"mime":"image\/png","size":44456,"href":"https:\/\/api.oyez.org\/sites\/default\/files\/elena-kagan-photo_0.png"},"length_of_service":1931,"identifier":"elena_kagan"}
  
  j2 = {"ID":15086,"name":"John G. Roberts, Jr.","href":"https:\/\/api.oyez.org\/people\/john_g_roberts_jr","last_name":"Roberts","roles":[{"id":2730,"type":"scotus_justice","date_start":1127970000,"date_end":0,"appointing_president":"George W. Bush","role_title":"Chief Justice of the United States","institution_name":"Supreme Court of the United States","href":"https:\/\/api.oyez.org\/preson_role\/scotus_justice\/2730"}],"thumbnail":{"id":32683,"mime":"image\/png","size":52305,"href":"https:\/\/api.oyez.org\/sites\/default\/files\/john_g_roberts_jr_0.png"},"length_of_service":3702,"identifier":"john_g_roberts_jr"}

  expected_cases = [c1, c2]
  expected_petitioners = [p1, p2]
  expected_respondents = [r1, r2]
  expected_votes = [v1, v2]

  def test_parse_scdb_case(self):
    for e, s in zip(self.expected_cases, self.test_strings):
      case = parse_scdb_case(make_dict(s))
      yield check_arguments, case, e
      
  def test_parse_male_justice(self):
    check_arguments(parse_justice(self.j2), {'name': 'John G. Roberts, Jr.', 'gender':'M', 'appointed_by': 'George W. Bush', 'oyez_id': 15086, 'date_start': date(2005, 9, 29)})
    
  def test_justice_labels(self):
    assert 'Elena Kagan' in female_justices

  def test_parse_female_justice(self):
    check_arguments(parse_justice(self.j1), {'name': 'Elena Kagan', 'gender':'F', 'appointed_by': 'Barack Obama', 'oyez_id': 15094, 'date_start': date(2010, 8, 7)})

  def test_parse_scdb_parties(self):
    parties = map(lambda x: parse_scdb_parties(make_dict(x)), self.test_strings)
    petitioners = map(lambda x: x[0], parties)
    respondents = map(lambda x: x[1], parties)
    for p, petitioner in zip(self.expected_petitioners, petitioners):
      yield check_arguments, p, petitioner
    for r, respondent in zip(self.expected_respondents, respondents):
      yield check_arguments, r, respondent
      
  def test_parse_sdcb_vote(self):
    id = 1
    for e, s in zip(self.expected_votes, self.test_strings):
      vote = parse_scdb_vote(make_dict(s), id)
      yield check_arguments, vote, e
      id += 1