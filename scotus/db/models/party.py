from sqlalchemy import Column, Integer, String, Unicode, UnicodeText, Date, Boolean, Enum, ForeignKey, String
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.hybrid import hybrid_property
from .base import Base

class Party(Base):
  __tablename__ = 'parties'
  
  name = Column(Unicode(150)) # scdb oyez
  side = Column('type', String(15), nullable=False) # scdb oyez
  kind = Column(Unicode(150)) # scdb
  location = Column(Unicode(50)) # scdb
  
  case_id =  Column(Integer, ForeignKey('cases.id'), nullable=False)
  case = relationship("Case")
  
  __mapper_args__ = {'polymorphic_on': side}
  
  def __repr__(self):
    return '<Party(docket={},{}: {})>'.format(self.case.docket, self.side, self.name)
  
class CanWin(object):
  @declared_attr
  def winner(cls):
    return Party.__table__.c.get('winner', Column(Boolean))
  
class Petitioner(Party, CanWin):
  __mapper_args__ = {'polymorphic_identity': 'petitioner'}
  
class Respondent(Party, CanWin):
  __mapper_args__ = {'polymorphic_identity': 'respondent'}
  
class Amicus(Party):
  __mapper_args__ = {'polymorphic_identity': 'amicus'}