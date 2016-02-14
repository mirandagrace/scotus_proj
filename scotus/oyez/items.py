# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
import jmespath
import json
from datetime import date
from scrapy.contrib.loader import ItemLoader
from scrapy.contrib.loader.processor import TakeFirst, MapCompose, Compose
from w3lib.html import remove_tags

class JsonItemLoader(ItemLoader):
  default_output_processor = TakeFirst()
  
  def __init__(self, json_object, item=None):
    self.json = json_object
    ItemLoader.__init__(self, item=item)
    
  def add_json(self, field_name, jmes_path, *processors, **kwargs):
    self.add_value(field_name, jmespath.search(jmes_path, self.json), *processors, **kwargs)
    
  def get_json(self, jmes_path, *processors, **kwargs):
    self.get_value(jmespath.search(jmes_path, self.json), *processors, **kwargs)
    
  def replace_json(self, field_name, jmes_path, *processors, **kwargs):
    self.add_value(field_name, jmespath.search(jmes_path, self.json), *processors, **kwargs)

html_input_processor = MapCompose(lambda x: x.encode('utf-8'), remove_tags)
integer_input_processor = MapCompose(lambda x: int(x))
timestamp_input_processor = MapCompose(lambda x: date.fromtimestamp(x))
text_output_processor = Compose(MapCompose(lambda x: x.strip()), TakeFirst())

class CaseItem(scrapy.Item):
  # define the fields for your item here like:
  name = scrapy.Field()
  granted_date = scrapy.Field()
  dec_date = scrapy.Field()
  facts = scrapy.Field(output_processor = text_output_processor)
  decision = scrapy.Field()
  docket = scrapy.Field()
  conclusion = scrapy.Field(output_processor = text_output_processor)
  oyez_id = scrapy.Field()
  volume = scrapy.Field()
  page = scrapy.Field()
  dec_type = scrapy.Field()
  prec_alt = scrapy.Field()
  dec_unconst = scrapy.Field()
  winning_party = scrapy.Field()
  questions = scrapy.Field(output_processor = text_output_processor)
  petitioner = scrapy.Field()
  respondent = scrapy.Field()
  description = scrapy.Field(output_processor = text_output_processor)
  
class CaseLoader(JsonItemLoader):
  default_item_class = CaseItem
  default_ouput_processor = TakeFirst()
  volume_in = integer_input_processor
  page_in = integer_input_processor
  questions_in = html_input_processor
  facts_in = html_input_processor
  conclusion_in = html_input_processor
  dec_date_in = timestamp_input_processor
  granted_date_in = timestamp_input_processor
  
  def load_case_data(loader):
    loader.add_json('name', 'name')
    loader.add_json('granted_date', "timeline[?event=='Granted'].dates[0]")
    loader.add_json('dec_date', "timeline[?event=='Decided'].dates[0]")
    loader.add_json('facts', 'facts_of_the_case')
    loader.add_json('questions', 'question')
    loader.add_json('docket', 'docket_number')
    loader.add_json('oyez_id', 'ID')
    loader.add_json('volume', 'citation.volume')
    loader.add_json('page', 'citation.page')
    loader.add_json('conclusion', 'conclusion')
    loader.add_json('petitioner', 'first_party')
    loader.add_json('respondent', 'second_party')
    return loader.load_item()

  def load_decision_data(l):
    l.add_json('dec_type', 'decision_type')
    l.add_json('prec_alt', 'alteration_of_precedent')
    l.add_json('winning_party', 'winning_party')
    l.add_json('dec_unconst', 'unconstitutionality')
    l.add_json('description', 'description')
    return l.load_item()

class AdvocateItem(scrapy.Item):
  side = scrapy.Field()
  name = scrapy.Field()
  case = scrapy.Field()

class TurnItem(scrapy.Item):
  speaker = scrapy.Field()
  text = scrapy.Field()
  context = scrapy.Field()





  



