# -*- coding: utf-8 -*-
import scrapy
from datetime import date
import json
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.contrib.loader import ItemLoader
from scrapy.selector import Selector
from ..items import CaseItem
from ..import models
from models import Case, Party
from .. import db

def strip_tags(s):
  return Selector(text=s).xpath('//text()').extract()

class CaseSpider(scrapy.Spider):
  name = "case"
  allowed_domains = ["oyez.org"]
  #terms = range(1955,2016) + ['1940-1955', '1900-1940', '1850-1900', '1789-1850']
  case_extractor = LinkExtractor(restrict_xpaths='//article[@class="content"]//li[@class="ng-scope"]')

  def __init__(self, term=[]):
    self.term = term
    self.session = db.Session()

  def start_requests(self):
    url = 'https://www.oyez.org/cases/' + str(self.term)
    yield scrapy.Request(url=url, callback=self.parse_term)

  def parse_term(self, response):
    links = case_extractor.extract_links(response)
    for link in link:
      yield scrapy.Request(url=link.url+'?labels=true', callback=self.parse_case, meta=response.meta)

  def add_case(self, case_data, citation, docket):
    case_dict = {'citation': citation, 'docket':docket}
    case_dict['name'] = case_data['name'].upcase().replace(' V. ', ' v. ')
    case = Case(**case_dict)
    petitioner = Party({'side':'petitioner', 'name':case_data['first_party']})
    respondent = Party({'side':'respondent', 'name':case_data['second_party']})
    if case_data['winning_side'] == petitioner.name:
      petitioner.winner = True
      respondent.winner = False
    elif case_data['winning_side'] == respondent.name:
      petitioner.winner = False
      respondent.winner = True
    else:
      pass
    case.petitioner = petitioner
    case.respondent = respondent
    return case

  def parse_case(self, response):
    ''' This function parses the case, and attempts to update the record in the database.
      @url https://api.oyez.org/cases/2014/14-556
      @returns items 1 1 

      #@url https://api.oyez.org/cases/1958/518
      #@returns items 1 1

      #@url https://api.oyez.org/cases/2015/14-770
      #@returns items 1 1

     '''
    case_data = json.loads(response.body)
    if case_data['citation']['volume'] != None and case_data['citation']['page'] != None:
      citation = case_data['citation']['volume'] + ' U.S. ' + str(case_data['citation']['page'])
      cases = self.session.query(Case).filter(Case.citation==citation.decode('utf-8')).all()
    else:
      citation = None
      cases = []
    if len(cases) != 1:
      docket = case_data['docket_number']
      #print case_data['docket_number']
      cases = self.session.query(Case).filter(Case.docket==docket).all()
    if len(cases) == 1:
      case = cases[0]
    elif '2015' in response.url:
      case = add_case(case_data, citation, case_data['docket_number'])
    else:
      raise ValueError, 'Unable to find case'
    #facts = strip_tags(case_data['facts_of_the_case'])[0]
    print case_data.keys()
    print case_data['decisions'][0].keys()
    print case_data['decisions'][0]['votes']









