from sqlalchemy import Column, Integer, String, Unicode, UnicodeText, Date, Boolean, Enum, ForeignKey
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.mutable import MutableComposite
from sqlalchemy.orm import relationship, composite
from .base import Base

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

  def __repr__(self):
    return "%r U.S. %r" % (self.volume, self.page)

  def __eq__(self, other):
    return isinstance(other, Citation) and \
        other.volume == self.volume and \
        other.page == self.page

  def __ne__(self, other):
    return not self.__eq__(other)

# class containing the information about the individual case
class Case(Base):
  __tablename__ = 'cases'
  
  # Identification Variables
  scdb_id = Column(Unicode(20), nullable=False, unique=True, index=True) # scdb
  oyez_id = Column(Integer, index=True) # oyez
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
  judgement = relationship('Judgement', back_populates='case', uselist=False)
  dissents = relationship('Dissent', back_populates='case')
  concurrences = relationship('Concurrence', back_populates='case')
  
  @property
  def winner(self):
    if self.winning_side == 'petitioner':
      return self.petitioner
    elif self.winning_side == 'respondent': # pragma: no branch
      return self.respondent
    return None # pragma: no cover
    
  @property
  def loser(self):
    if self.losing_side == 'petitioner':
      return self.petitioner
    elif self.losing_side == 'respondent': # pragma: no branch
      return self.respondent
    return None # pragma: no cover
    
  def __repr__(self):
    return '<Case(docket={}, name={})>'.format(self.docket, self.name)
    
class Question(Base):
  __tablename__ = 'questions'
  
  text = Column(UnicodeText) # oyez
  disposition = Column(Unicode(100)) # oyez
  
  case_id = Column(Integer, ForeignKey('cases.id'), nullable=False)
  case = relationship('Case', back_populates='questions')