# -*- coding: utf-8 -*-
import scrapy
import json
import jmespath
from datetime import date
from scrapy.selector import Selector
from w3lib.url import url_query_parameter
from ..items import CaseItem, CaseLoader, VoteItem, VoteLoader

  
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
    loader = CaseLoader(json_object=json_response)
    case = loader.load_case_data()
    case_id = case['oyez_id']
    decision_url = jmespath.search('decisions[0].href', json_response)
    if decision_url != None:
      results.append(scrapy.Request(url=decision_url, callback=self.parse_decision, meta={'case': case}))
    else:
      results.append(case)
    return results
    #advocates = json_response['advocates']
    #for advocate in advocates:
      
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










