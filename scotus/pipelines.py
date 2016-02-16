# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.exceptions import DropItem
from .db import DB
from .db.models import *
from .items import CaseItem, VoteItem, AdvocateItem, ArgumentItem, SectionItem 
from .items import TurnItem, JusticeTurnItem, AdvocateTurnItem, AlchemyItem

class OyezPipeline(object):
  classes = [CaseItem, VoteItem, AdvocateItem, ArgumentItem, SectionItem, TurnItem, JusticeTurnItem, AdvocateTurnItem]

  def __init__(self, db):
    self.db = db
    self.session = None

  def open_session(self):
    self.session = self.db.Session()

  def close_session(self):
    self.session.close()

  @classmethod
  def from_crawler(cls, crawler):
    return cls(DB(crawler.settings.get('DEFAULT_DB')))

  def open_spider(self, spider):
    self.open_session()

  def close_spider(self, spider):
    self.close_session()

  def process_item(self, item, spider):
    if isinstance(item, AlchemyItem):
      try:
        item.send(self.session)
        self.session.commit()
      except:
        self.session.rollback()
        raise
    return item