from sqlalchemy import Column, Integer, String, Unicode, UnicodeText, Date, Boolean, Enum, ForeignKey
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.mutable import MutableComposite
from sqlalchemy.orm import relationship, composite
from sqlalchemy import bindparam
from .base import Base, bakery, OyezIdMixin
from sqlalchemy import or_, and_

class Citation(MutableComposite):
  def __init__(self, volume, page):
    self.volume = volume
    self.page = page

  def __composite_values__(self):
    return self.volume, self.page
      
  
  def __setattr__(self, key, value):
    "Intercept set events"

    # set the attribute
    object.__setattr__(self, key, value)

    # alert all parents to the change
    self.changed()

  def __repr__(self): #pragma: no cover
    return "%r U.S. %r" % (self.volume, self.page)

  def __eq__(self, other):
    return isinstance(other, Citation) and \
        other.volume == self.volume and \
        other.page == self.page

  def __ne__(self, other):
    return not self.__eq__(other)

# class containing the information about the individual case
class Case(Base, OyezIdMixin):
  __tablename__ = 'cases'
  
  # Identification Variables
  scdb_id = Column(Unicode(20), index=True) # scdb
  volume = Column(Integer) # scdb oyez
  page = Column(Integer) # scdb oyez
  citation = composite(Citation, volume, page) # scdb
  docket = Column(Unicode(20), index=True) # scdb oyez
  name = Column(Unicode(150)) # scdb oyez
  
  # Procedural Variables
  jurisdiction = Column(Unicode(20)) # scdb
  cert_reason = Column(Unicode(20)) # scdb
  admin = Column(Unicode(100)) # scdb
  admin_loc = Column(Unicode(50)) # scdb
  origin = Column(Unicode(100)) # scdb
  orig_loc = Column(Unicode(50)) # scdb
  lower_court = Column(Unicode(100)) # scdb
  low_court_loc = Column(Unicode(50)) # scdb
  low_court_disp = Column(Unicode(20)) # scdb
  low_court_disp_dir = Column(Unicode(20)) # scdb
  disposition = Column(Unicode(20)) # scdb
  
  # Date Variables
  dec_date = Column(Date) # scdb oyez
  granted_date = Column(Date) # oyez
  
  # Decision Variables
  dec_dir = Column(Unicode(20)) # scdb
  dec_type = Column(Unicode(20)) # scdb oyez
  dec_unconst = Column(Boolean) # scdb oyez
  prec_alt = Column(Boolean) # scdb oyez 
  winning_side = Column(Unicode(20)) # scdb oyez
  losing_side = Column(Unicode(20)) # scdb oyez
  
  # Text Variables
  syllabus = Column(UnicodeText) # casetext
  holding = Column(UnicodeText) # casetext
  facts = Column(UnicodeText) # oyez
  conclusion = Column(UnicodeText) # oyez
  description = Column(UnicodeText) # oyez
  
  # Relationships
  parties = relationship('Party', back_populates='case')
  petitioner = relationship('Petitioner', back_populates = 'case', uselist=False)
  respondent = relationship('Respondent', back_populates='case', uselist=False) 
  amici = relationship('Amicus', back_populates='case')
  
  votes = relationship('Vote', back_populates='case')
  justices = association_proxy('votes', 'justice')
  
  questions = relationship('Question', back_populates='case')
  
  opinions = relationship('Opinion', back_populates='case')

  arguments = relationship('Argument', back_populates='case')
  case_advocacies = relationship('Advocacy', back_populates='case')
  advocates = association_proxy('case_advocacies', 'advocate')
  
  @property
  def winner(self):
    if self.winning_side == 'petitioner':
      return self.petitioner
    elif self.winning_side == 'respondent': 
      return self.respondent
    return None
    
  @property
  def loser(self):
    if self.losing_side == 'petitioner':
      return self.petitioner
    elif self.losing_side == 'respondent': 
      return self.respondent
    return None
    
  def __repr__(self): #pragma: no cover
    return '<Case(docket={}, name={})>'.format(self.docket, self.name)
    
  @classmethod
  def search_for_scraped(cls, session, docket=None, volume=None, page=None):
    baked_query = bakery(lambda session: session.query(cls))
    baked_query += lambda q: q.filter(or_(cls.docket == bindparam('docket'), 
                                          and_(cls.volume == bindparam('volume'),
                                               cls.page == bindparam('page'))))
    result = baked_query(session).params(docket=docket, volume=volume, page=page).one_or_none()
    return result

  @classmethod
  def search_by_oyez_id(cls, session, oyez_id=None):
    baked_query = bakery(lambda session: session.query(cls))
    baked_query += lambda q: q.filter(cls.oyez_id == bindparam('oyez_id'))
    result = baked_query(session).params(oyez_id=oyez_id).one_or_none()
    return result
    
    
class Question(Base):
  __tablename__ = 'questions'
  
  text = Column(UnicodeText) # oyez
  disposition = Column(Unicode(100)) # oyez
  
  case_id = Column(Integer, ForeignKey('cases.id'), nullable=False)
  case = relationship('Case', back_populates='questions')