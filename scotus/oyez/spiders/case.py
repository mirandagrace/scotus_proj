# -*- coding: utf-8 -*-
import scrapy
from datetime import date
import json
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.contrib.loader import ItemLoader
from scrapy.selector import Selector
from ..items import CaseItem

def strip_tags(s):
  return Selector(text=s).xpath('//text()').extract()

class CaseSpider(scrapy.Spider):
  name = "case"
  allowed_domains = ["oyez.org"]
  #terms = range(1955,2016) + ['1940-1955', '1900-1940', '1850-1900', '1789-1850']
  case_extractor = LinkExtractor(restrict_xpaths='//article[@class="content"]//li[@class="ng-scope"]')

  def __init__(self, term=[]):
    self.term = term

  def start_requests(self):
    url = 'https://www.oyez.org/cases/' + str(self.term)
    yield scrapy.Request(url=url, callback=self.parse_term)

  def parse_term(self, response):
    links = case_extractor.extract_links(response)
    for link in link:
      yield scrapy.Request(url=link.url+'?labels=true', callback=self.parse_case, meta=response.meta)

  def parse_case(self, response):
    case_data = json.loads(response.body)
    return









