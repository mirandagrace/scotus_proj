# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
import jmespath
import json
import dateutil.parser
from datetime import date, datetime
from scrapy.contrib.loader import ItemLoader
from scrapy.contrib.loader.processor import TakeFirst, MapCompose, Compose, Identity, Join
from .db.models import *
from sqlalchemy import bindparam
from w3lib.html import remove_tags

class JsonItemLoader(ItemLoader):
  default_output_processor = TakeFirst()
  
  def __init__(self, json_object, item=None):
    self.json = json_object
    ItemLoader.__init__(self, item=item)
    
  def add_json(self, field_name, jmes_path, *processors, **kwargs):
    self.add_value(field_name, jmespath.search(jmes_path, self.json), *processors, **kwargs)
    
  def get_json(self, jmes_path, *processors, **kwargs):
    return self.get_value(jmespath.search(jmes_path, self.json), *processors, **kwargs)
    
  def replace_json(self, field_name, jmes_path, *processors, **kwargs):
    self.add_value(field_name, jmespath.search(jmes_path, self.json), *processors, **kwargs)

def safe_int(x):
  try:
    return int(x)
  except:
    return None

html_input_processor = MapCompose(lambda x: x.encode('utf-8'), remove_tags)
integer_input_processor = MapCompose(lambda x: safe_int(x))
timestamp_input_processor = MapCompose(lambda x: date.fromtimestamp(x))
text_output_processor = Compose(MapCompose(lambda x: x.strip()), TakeFirst())

class AlchemyItem(scrapy.Item):
  Model = None
  update_fields = frozenset([])
  exclude_model_fields = frozenset([])
  search_fields = frozenset([])
  
  def clean(self): #pragma: no cover
    pass
    
  def on_add_record(self, session, record):
    pass
    
  def on_update_record(self, session, record):
    pass

  def on_send_record(self, session, record):
    pass
    
  def _add_args(self):
    return {k:v for k,v in dict(self).items() if k not in self.exclude_model_fields and v!=None}
    
  def _add_record(self, session):
    record = self.Model(**self._add_args())
    self.on_add_record(session, record)
    session.add(record)
    return record
    
  def _get(self, session):
    return self.Model.search_for_scraped(session, **self._search_args())
    
  def _search_args(self):
    return {k:v for k,v in dict(self).items() if k in self.search_fields and v!=None}
    
  def send(self, session):
    self.clean()
    item_obj = self._get(session)
    try:
      if item_obj == None:
        item_obj = self._add_record(session)
      else:
        self._update_record(session, item_obj)
      session.commit()
    except:
      session.rollback()
      raise
    try:
      self.on_send_record(session, item_obj)
      session.commit()
    except:
      session.rollback()
      raise
    return item_obj
      
  def _update_args(self):
    return {k:v for k,v in dict(self).items() if k in self.update_fields and v}
    
  def _update_record(self, session, record):
    for k, v in self._update_args().items():
      if getattr(record, k) == None:
        setattr(record, k, v)
    self.on_update_record(session, record)
   
class CaseItem(AlchemyItem):
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
  citation = scrapy.Field()
  dec_type = scrapy.Field()
  prec_alt = scrapy.Field()
  dec_unconst = scrapy.Field()
  winning_party = scrapy.Field()
  winning_side = scrapy.Field()
  losing_side = scrapy.Field()
  questions = scrapy.Field(output_processor = text_output_processor)
  petitioner = scrapy.Field()
  respondent = scrapy.Field()
  description = scrapy.Field(output_processor = text_output_processor)
  
  Model = Case
  update_fields = frozenset(['oyez_id', 'decision', 'granted_date', 'conclusion', 'description', 'winning_side',
                             'losing_side', 'facts', 'decision', 'dec_type', 'prec_alt', 'volume', 'page', 'docket',
                             'name', 'winning_side', 'losing_side'])
  exclude_model_fields = frozenset(['questions', 'petitioner', 'respondent', 'winning_party'])
  search_fields = frozenset(['docket', 'volume', 'page'])
  
  def clean(item):
    wp = item.get('winning_party', '').lower()
    if wp in item.get('petitioner', '').lower():
      item['winning_side'] = u'petitioner'
      item['losing_side'] = u'respondent'
    elif wp in item.get('respondent', '').lower():
      item['winning_side'] = u'respondent'
      item['losing_side'] = u'petitioner'
    else:
      pass
      
  def on_add_record(self, session, record):
    wp = self.get('winning_party', '')
    if wp == 'petitioner':
      record.petitioner = Petitioner(name=self.get('petitioner', None), winner=True)
      record.respondent = Respondent(name=self.get('respondent', None), winner=False)
    elif wp == 'respondent':
      record.petitioner = Petitioner(name=self.get('petitioner', None), winner=False)
      record.respondent = Respondent(name=self.get('respondent', None), winner=True)
    else:
      record.respondent = Respondent(name=self.get('respondent', None))
      record.petitioner = Petitioner(name=self.get('petitioner', None))
      
  def on_update_record(self, session, record):
    wp = self.get('winning_party', '')
    if wp == 'petitioner':
      record.petitioner.winner=True
      record.respondent.winner=False
    elif wp == 'respondent':
      record.petitioner.winner=False
      record.respondent.winner=True
    else:
      pass
    
  def on_send_record(self, session, record):
    if len(record.questions) == 0:
      questions = self.get('questions', None)
      if questions != None:
        questions = map(lambda x: x.strip('0123456789().').strip(), questions.split('\n'))
      conclusions = self.get('conclusion', None)
      if conclusions != None:
        conclusions = conclusions.split('.', 1)[0]
        conclusions = conclusions.split(' and ', 1)
        if len(conclusions) > 1:
          last = [conclusions[1]]
        else:
          last = []
        conclusions = conclusions[0].split(',')+last
      else:
        conclusions = []
      try:
        for q, c in zip(questions, conclusions):
          record.questions.append(Question(text=q, disposition=c.lower().strip()))
      except:
        pass
  
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

class VoteItem(AlchemyItem):
  justice_oyez_id = scrapy.Field()
  case_oyez_id = scrapy.Field()
  vote = scrapy.Field()
  opinion_written = scrapy.Field()
  opinions_joined = scrapy.Field()

  Model = Vote
  update_fields = frozenset(['vote'])
  exclude_model_fields = frozenset(['justice_oyez_id', 'opinion_written', 'opinions_joined', 'case_oyez_id', 'opinion_kind'])
  search_fields = frozenset(['justice_oyez_id', 'case_oyez_id'])
  
  def clean(self):
    pass
    
  def on_add_record(self, session, record):
    record.case_id = Case.search_by_oyez_id(session, self.get('case_oyez_id')).id
    record.justice_id = Justice.search_by_oyez_id(session, self.get('justice_oyez_id')).id
    
  def on_send_record(self, session, record):
    case = record.case
    opinion_written =  self.get('opinion_written', None)
    if opinion_written != None and opinion_written != 'none':
      opinion = Opinion.search_by_author_vote(session, record.case_id, record.justice_id)
      if opinion == None:
        opinion = Opinion(case_id = case.id, kind=opinion_written)
        ow = OpinionWritten(opinion=opinion, justice=record.justice)
        session.add(opinion)
        session.add(ow)
      else:
        opinion.kind = opinion_written

    justices_joined = self.get('opinions_joined', [])
    for justice_joined_oyez_id in justices_joined:
      justice_joined = Justice.search_by_oyez_id(session, justice_joined_oyez_id)
      j_opinion = Opinion.search_by_author_vote(session, case.id, justice_joined.id)
      if j_opinion == None:
        j_opinion = Opinion(case=case,)
        session.add(j_opinion)
        ow = OpinionWritten(opinion=j_opinion, justice= justice_joined)
        session.add(ow)
      oj = OpinionJoined(opinion=j_opinion, justice = record.justice)
      session.add(oj)


class VoteLoader(JsonItemLoader):
  default_item_class = VoteItem
  default_ouput_processor = TakeFirst()
  opinions_joined_out = Identity()

  def load_vote_data(self, case_id):
    self.add_value('case_oyez_id', case_id)
    self.add_json('justice_oyez_id', 'member.ID')
    self.add_json('vote', 'vote')
    self.add_json('opinion_written', 'opinion_type')
    self.add_json('opinions_joined', 'joining[*].ID')
    return self.load_item()

class AdvocateItem(AlchemyItem):
  description = scrapy.Field()
  side = scrapy.Field()
  role = scrapy.Field()
  name = scrapy.Field()
  case_oyez_id = scrapy.Field()
  oyez_id = scrapy.Field()
  gender = scrapy.Field()

  Model = Advocate
  update_fields = frozenset([])
  exclude_model_fields = frozenset(['description', 'case_oyez_id', 'role', 'side'])
  search_fields = frozenset(['oyez_id'])
  
  def clean(self):
    description = self.get('description', '')
    if 'petitioner' in description.lower() or 'appellant' in description.lower() or self.get('role', None) == 'party1':
      self['side'] = u'petitioner'
    elif 'respondent' in description.lower() or 'appellee' in description.lower()or self.get('role', None) == 'party2':
      self['side'] = u'respondent'
    else:
      pass
    
  def on_send_record(self, session, record):
    case = Case.search_by_oyez_id(session, self.get('case_oyez_id'))
    advocacy = Advocacy.search_for_scraped(session, case.id, advocate_oyez_id = self.get('oyez_id', None))
    if advocacy == None:
      advocacy = Advocacy(side=self.get('side', None), role=self.get('role',None), case_id=case.id)
      advocacy.advocate = record
      session.add(advocacy)
    else:
      if not advocacy.side:
        advocacy.side = self.get('side', None)
      if not advocacy.role:
        advocacy.role = self.get('role', None)
      
class AdvocateLoader(JsonItemLoader):
  default_item_class = AdvocateItem
  default_ouput_processor = TakeFirst()

  def load_advocate_data(self, case_id, gp=None):
    if gp != None:
      self.add_json('gender', 'advocate.name', gp)
    self.add_value('case_oyez_id', case_id)
    self.add_json('description', 'advocate_description')
    self.add_json('role', 'advocate_role.value')
    self.add_json('name', 'advocate.name')
    self.add_json('oyez_id', 'advocate.ID')
    return self.load_item()

  def load_speaking_data(self, case_id, gp=None):
    if gp != None:
      self.add_json('gender', 'speaker.name', gp)
    self.add_value('case_oyez_id', case_id)
    self.add_json('name', 'speaker.name')
    self.add_json('oyez_id', 'speaker.ID')
    return self.load_item()

class ArgumentItem(AlchemyItem):
  case_oyez_id = scrapy.Field()
  date = scrapy.Field()
  oyez_id = scrapy.Field()

  Model = Argument
  update_fields = frozenset(['date'])
  exclude_model_fields = frozenset(['case_oyez_id'])
  search_fields = frozenset(['oyez_id'])
    
  def on_add_record(self, session, record):
    case = Case.search_by_oyez_id(session, self.get('case_oyez_id'))
    record.case = case

class ArgumentLoader(JsonItemLoader):
  default_item_class = ArgumentItem
  default_output_processor = TakeFirst()
  date_in = MapCompose(lambda x: dateutil.parser.parse(x).date())

  def load_argument_data(self, case_id):
    self.add_value('case_oyez_id', case_id)
    self.add_json('oyez_id', "id")
    self.add_json('date', 'title', re=r'Oral Argument - ([A-Za-z 0-9,]+) ')
    return self.load_item()

class SectionItem(AlchemyItem):
  argument_oyez_id = scrapy.Field()
  number = scrapy.Field()
  advocate_oyez_id = scrapy.Field()

  Model = Section
  update_fields = frozenset([])
  exclude_model_fields = frozenset(['argument_oyez_id', 'advocate_oyez_id'])
  search_fields = frozenset(['argument_oyez_id', 'number'])

  def on_add_record(self, session, record):
    argument = Argument.search_by_oyez_id(session, self.get('argument_oyez_id'))
    record.argument = argument

  def on_send_record(self, session, record):
    advocate_oyez_id = self.get('advocate_oyez_id', None)
    if advocate_oyez_id:
      case = record.argument.case
      advocacy = Advocacy.search_for_scraped(session, case_id=case.id, advocate_oyez_id=advocate_oyez_id)
      record.advocacy = advocacy


class SectionLoader(JsonItemLoader):
  default_item_class = SectionItem
  default_output_processor = TakeFirst()

  def load_section_data(self, argument_id, number):
    self.add_value('argument_oyez_id', argument_id)
    self.add_value('number', number)
    return self.load_item()

  def load_advocate_owner(self, advocate_oyez_id):
    self.add_value('advocate_oyez_id', advocate_oyez_id)
    return self.load_item()

class TurnItem(AlchemyItem):
  number = scrapy.Field()
  section_number = scrapy.Field()
  argument_oyez_id = scrapy.Field()
  text = scrapy.Field()
  time_start = scrapy.Field()
  time_end = scrapy.Field()

  Model = Turn
  update_fields = frozenset([])
  exclude_model_fields = frozenset(['section_number', 'argument_oyez_id'])
  search_fields = frozenset(['number', 'section_number', 'argument_oyez_id'])

  def set_section(self, session, record):
    section = Section.search_for_scraped(session, argument_oyez_id=self.get('argument_oyez_id'), number=self.get('section_number'))
    record.section = section
    
  def on_add_record(self, session, record):
    self.set_section(session, record)

class TurnLoader(JsonItemLoader):
  default_item_class = TurnItem
  default_output_processor = TakeFirst()
  text_in = MapCompose(lambda x: x.encode('utf-8'), remove_tags, lambda x: x.strip())
  text_out = Join(u' ')

  def _load_base_data(self, argument_id, section_number, turn_number):
    self.add_value('argument_oyez_id', argument_id)
    self.add_value('section_number', section_number)
    self.add_value('number', turn_number)
    self.add_json('time_start', 'start')
    self.add_json('time_end', 'stop')
    self.add_json('text', 'text_blocks[*].text')
    return

  def load_turn_data(self, argument_id, section_number, turn_number):
    self._load_base_data(argument_id, section_number, turn_number)
    return self.load_item()

class JusticeTurnItem(TurnItem):
  justice_oyez_id = scrapy.Field()

  Model = JusticeTurn
  exclude_model_fields = frozenset(['section_number', 'argument_oyez_id', 'justice_oyez_id'])

  def on_add_record(self, session, record):
    self.set_section(session, record)
    justice = Justice.search_by_oyez_id(session, self.get('justice_oyez_id'))
    record.justice = justice

class JusticeTurnLoader(TurnLoader):
  default_item_class = JusticeTurnItem

  def load_turn_data(self, argument_id, section_number, turn_number):
    self._load_base_data(argument_id, section_number, turn_number)
    self.add_json('justice_oyez_id', 'speaker.ID')
    return self.load_item()

class AdvocateTurnItem(TurnItem):
  advocate_oyez_id = scrapy.Field()

  Model = AdvocateTurn
  exclude_model_fields = frozenset(['section_number', 'argument_oyez_id', 'advocate_oyez_id'])

  def on_add_record(self, session, record):
    self.set_section(session, record)
    advocate = Advocate.search_by_oyez_id(session, self.get('advocate_oyez_id'))
    record.advocate = advocate

class AdvocateTurnLoader(TurnLoader):
  default_item_class = AdvocateTurnItem

  def load_turn_data(self, argument_id, section_number, turn_number):
    self._load_base_data(argument_id, section_number, turn_number)
    self.add_json('advocate_oyez_id', 'speaker.ID')
    return self.load_item()

def turn_loader_factory(turn_json):
  speaker = turn_json['speaker']
  role = jmespath.search('speaker.roles', turn_json)
  if role == None and speaker !=None:
    return AdvocateTurnLoader(turn_json)
  elif role:
    return JusticeTurnLoader(turn_json)
  else:
    return TurnLoader(turn_json)
  






  



