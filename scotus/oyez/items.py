# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.contrib.loader import ItemLoader
from scrapy.contrib.loader.processor import TakeFirst

class CaseItem(scrapy.Item):
  # define the fields for your item here like:
  name = scrapy.Field()
  granted_date = scrapy.Field()
  dec_date = scrapy.Field()
  facts = scrapy.Field()
  decision = scrapy.Field()
  holding = scrapy.Field()
  syllabus = scrapy.Field()
  docket = scrapy.Field()
  citation = scrapy.Field()
  conclusion = scrapy.Field()

class AdvocateItem(scrapy.Item):
  side = scrapy.Field()
  name = scrapy.Field()

class TurnItem(scrapy.Item):
  speaker = scrapy.Field()
  text = scrapy.Field()
  context = scrapy.Field()

class QuestionItem(scrapy.Item):
  text = scrapy.Field()
  disposition = scrapy.Field()





  



