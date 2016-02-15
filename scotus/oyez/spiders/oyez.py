# -*- coding: utf-8 -*-
import scrapy
import json
import jmespath
from datetime import date
from scrapy.selector import Selector
from w3lib.url import url_query_parameter
from ..items import CaseItem, CaseLoader, VoteItem, VoteLoader, AdvocateLoader

  
class OyezSpider(scrapy.Spider):
  name = "oyez"
  allowed_domains = ["oyez.org"]

  def __init__(self, term=2014):
    self.term = term
    
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
    for case in cases:
      url = case['href']
      yield scrapy.Request(url=url, callback=self.parse_case)
    if len(cases)>=30:
      page = int(url_query_parameter(response.url, 'page')) + 1
      yield scrapy.Request(url=self.term_url(page), callback=self.parse_term)

  def parse_case(self, response):
    '''
      @url https://api.oyez.org/cases/2014/14-556
      @returns requests 1 1
      @returns items 0 0
    '''
    results = []
    json_response = json.loads(response.body)

    # load case
    loader = CaseLoader(json_object=json_response)
    case = loader.load_case_data()

    # if there is explicit decision data, go and get it; otherwise add the case to the results
    case_id = case['oyez_id']
    decision_url = jmespath.search('decisions[0].href', json_response)
    if decision_url != None:
      results.append(scrapy.Request(url=decision_url, callback=self.parse_decision, meta={'case': case}))
    else:
      results.append(case)
    advocate_links = jmespath.search('advocates[*].href', json_response)
    for advocate_link in advocate_links:
      results.append(scrapy.Request(url=advocate_link, callback=self.parse_advocate, meta={'case_id':case_id}))
    return results
      
  def parse_decision(self, response):
    '''
      @url https://api.oyez.org/case_decision/case_decision/16363
      @returns requests 0 0
      @returns items 10 10
    '''
    results = []
    json_response = json.loads(response.body)
    l = CaseLoader(json_object=json_response, item=response.meta.get('case', CaseItem()))
    case = l.load_decision_data()
    results.append(case)
    votes_json = json_response['votes']
    for vote_json in votes_json:
      results.append(VoteLoader(vote_json).load_vote_data(case.get('oyez_id', None)))
    return results

  def parse_advocate(self, response):
    '''
      @url https://api.oyez.org/case_advocate/case_advocate/20934
      @returns requests 0 0
      @returns items 1 1
      @scrapes advocate_oyez_id name role description
    '''
    json_response = json.loads(response.body)
    return AdvocateLoader(json_response).load_advocate_data(response.meta.get('case_id', None))










