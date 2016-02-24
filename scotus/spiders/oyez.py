# -*- coding: utf-8 -*-
import scrapy
import json
import jmespath
from datetime import date
from scrapy.selector import Selector
from w3lib.url import url_query_parameter
from ..settings import TEST_DB, DEFAULT_DB
from ..items import CaseItem, CaseLoader, VoteItem, VoteLoader, AdvocateLoader, AdvocateTurnItem
from ..items import ArgumentLoader, SectionLoader, turn_loader_factory
from ..db.models import *
from ..db import DB
import sexmachine.detector as gender

  
class OyezSpider(scrapy.Spider):
  name = "oyez"
  allowed_domains = ["oyez.org"]

  def gender_processor(self, name):
    first_name = name.split()
    gender =  self.detector.get_gender(first_name)
    if gender == 'female':
      return u'F'
    elif gender == 'male':
      return u'M'
    else:
      return None


  def __init__(self, term=2014, test=False):
    self.term = term
    self.detector = gender.Detector()
    if test:
      self.db = DB(TEST_DB)
    else:
      self.db = DB(DEFAULT_DB)
    self.session = self.db.Session()
    
  def term_url(self, page):
    return 'https://api.oyez.org/cases?filter=term:{}&page={}'.format(self.term, page)

  def start_requests(self):
    url = self.term_url(0)
    return[scrapy.Request(url=url, callback=self.parse_term, meta={'page':0})]

  def parse_term(self, response):
    '''
      @url https://api.oyez.org/cases?filter=term:2014&page=0
      @returns requests 31 31
      @returns items 0 0
    '''
    cases = json.loads(response.body)
    results = []
    for case in cases:
      url = case['href']
      results.append(scrapy.Request(url=url, callback=self.parse_case))
    if len(cases)>=30:
      page = int(url_query_parameter(response.url, 'page')) + 1
      results.append(scrapy.Request(url=self.term_url(page), callback=self.parse_term))
    return results

  def parse_case(self, response):
    '''
      @url https://api.oyez.org/cases/2014/14-556
      @returns requests 8 8
      @returns items 0 0
    '''
    results = []
    json_response = json.loads(response.body)

    # load case
    loader = CaseLoader(json_object=json_response)
    case = loader.load_case_data()
    case.send(self.session)
    case_id = case['oyez_id']


    # if there is explicit decision data, go and get it; otherwise add the case to the results
    decision_url = jmespath.search('decisions[0].href', json_response)
    if decision_url != None:
      results.append(scrapy.Request(url=decision_url, callback=self.parse_decision, meta={'case': case}))

    # if there is advocacy data, go and get it
    advocate_links = jmespath.search('advocates[*].href', json_response)
    if advocate_links == None:
      advocate_links = []
    for advocate_link in advocate_links:
      results.append(scrapy.Request(url=advocate_link, callback=self.parse_advocate, meta={'case_id':case_id}))

    # if there is transcript data, go and get it
    transcript_links = jmespath.search('oral_argument_audio[*].href', json_response)
    for transcript_link in transcript_links:
      results.append(scrapy.Request(url=transcript_link, callback=self.parse_transcript, meta={'case_id':case_id}))
    return results
      
  def parse_decision(self, response):
    '''
      @url https://api.oyez.org/case_decision/case_decision/16363
      @returns requests 0 0
    '''
    json_response = json.loads(response.body)

    l = CaseLoader(json_object=json_response, item=response.meta.get('case', CaseItem()))
    case = l.load_decision_data()
    case.send(self.session)

    votes_json = json_response['votes']
    for vote_json in votes_json:
      vote = VoteLoader(vote_json).load_vote_data(case.get('oyez_id', None))
      vote.send(self.session)
    return

  def parse_advocate(self, response):
    '''
      @url https://api.oyez.org/case_advocate/case_advocate/20934
      @returns requests 0 0
    '''
    json_response = json.loads(response.body)
    loader = AdvocateLoader(json_response)
    loader.add_json('gender', 'name', self.gender_processor)
    advocate = loader.load_advocate_data(response.meta.get('case_id', None))
    advocate.send(self.session)
    return 


  def parse_transcript(self, response):
    '''
      @url http://api.oyez.org/case_media/oral_argument_audio/16189
      @returns items 155 155
      @returns requests 0 0
    '''
    # 1 argument 4 sections  # 18 20 105 4 # 3 advocates
    results = []
    advocate_ids_seen = set([])
    json_response = json.loads(response.body)
    case_oyez_id = response.meta.get('case_id', None)

    # parse the arguments
    argument = ArgumentLoader(json_response).load_argument_data(case_oyez_id)
    argument_oyez_id = argument['oyez_id']
    argument.send(self.session)

    # parse the sections
    sections = jmespath.search('transcript.sections', json_response)
    if sections == None:
      sections = []
    for section_number, section_json in enumerate(sections):
      section_loader = SectionLoader(section_json)
      section_item = section_loader.load_section_data(argument_oyez_id, section_number)
      section_item.send(self.session)

      # parse turns
      turns = jmespath.search('turns', section_json)
      section = None # keep track of if we've found the advocate owner of the section yet
      for turn_number, turn_json in enumerate(turns):
        # load turn data
        turn = turn_loader_factory(turn_json).load_turn_data(argument_oyez_id, section_number, turn_number)
        if turn.__class__ == AdvocateTurnItem:
          advocate_id = turn['advocate_oyez_id']
          if advocate_id not in advocate_ids_seen: # if we haven't seen the advocate before
            advocate = AdvocateLoader(turn_json).load_speaking_data(case_oyez_id) # load the advocate data
            advocate.send(self.session)
            advocate_ids_seen.add(advocate['oyez_id']) # update the seen set
          else:
            pass
          if section == None: # if we haven't assigned a primary advocate to the section yet
            section = section_loader.load_advocate_owner(advocate_id)
            section.send(self.session)
          else:
            pass
        else:
          pass
        turn.send(self.session)
    return results










