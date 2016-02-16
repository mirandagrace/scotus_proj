# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.exceptions import DropItem
from sqlalchemy import or_, and_
from .db import DB
from .db.models import *
from .items import CaseItem, VoteItem, AdvocateItem, ArgumentItem, SectionItem, TurnItem, JusticeTurnItem, AdvocateTurnItem

def add_oyez_case(session, case_dict):
  petitioner_name = case_dict['petitioner']
  respondent_name = case_dict['respondent']
  del case_dict['questions']
  del case_dict['petitioner']
  del case_dict['respondent']
  del case_dict['winning_party']
  case = Case(**case_dict)
  session.add(case)
  case.petitioner = Petitioner(name=petitioner_name)
  case.respondent = Respondent(name=respondent_name)
  return case

class CasePipeline(object):
  def process_item(self, item, spider):
    if item.__class__ == CaseItem:
      wp = item.get('winning_party', '')
      if wp in item.get('petitioner', ''):
        item['winning_side'] = 'petitioner'
        item['losing_side'] = 'respondent'
      elif wp in item.get('respondent', ''):
        item['winning_side'] = 'respondent'
        item['losing_side'] = 'petitioner'
      else:
        pass
      item['winning_party'] = None
    else:
      pass
    return item

class OyezPipeline(object):
  classes = [CaseItem, VoteItem, AdvocateItem, ArgumentItem, SectionItem, TurnItem, JusticeTurnItem, AdvocateTurnItem]

  def __init__(self, db_file):
    self.db = DB(db_file)
    self.process_dict = {
      'CaseItem': self.process_case
    }
    self.session = None

  def open_session(self):
    self.session = self.db.Session()

  def close_session(self):
    self.session.close()

  @classmethod
  def from_crawler(cls, crawler):
    return cls(crawler.settings.get('DEFAULT_DB'))

  def open_spider(self, spider):
    self.session = self.db.Session()

  def close_spider(self, spider):
    self.session.close()

  def process_item(self, item, spider):
    try:
      self.process_dict.get(item.__class__.__name__, lambda x,y: x)(item, spider)
      self.session.commit()
    except:
      self.session.rollback()
      raise 
    return item

  def process_case(self, item, spider):
    case = self.session.query(Case).filter(or_(Case.docket==item.get('docket', None), 
                                           and_(Case.volume==item.get('volume', None), 
                                                Case.page==item.get('page', None)))).one_or_none()
    if case == None:
      case = add_oyez_case(self.session, dict(item))
    else:
      case.oyez_id = item['oyez_id']
      case.facts = item.get('facts', None)
      case.granted_date = item.get('granted_date', None)
      case.conclusion = item.get('conclusion', None)
      case.description = item.get('description', None)

    questions = item.get('questions', None)
    if questions != None:
      questions = map(lambda x: x.strip('0123456789()').strip(), questions.split('\n'))
    conclusions = item.get('conclusion', None)
    if conclusions != None:
      conclusions = conclusions.split('.', 1)[0].split(',')
    for q, c in zip(questions, conclusions):
      case.questions.append(Question(text=q, disposition=c.lower()))
    return item