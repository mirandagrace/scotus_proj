from sqlalchemy import Column, Integer, String, Unicode, UnicodeText, Date, Boolean, Enum, ForeignKey
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship
from base import Base

# class containing the information about the individual case
class Case(Base):
  __tablename__ = 'cases'
  
  # Identification Variables
  scdb_id = Column(Unicode(20), nullable=False, unique=True, index=True)
  citation = Column(Unicode(100))
  docket = Column(Unicode(20), nullable=False, index=True)
  name = Column(Unicode(150), index=True)
  
  # Procedural Variables
  jurisdiction = Column(Unicode(20))
  cert_reason = Column(Unicode(20))
  admin = Column(Unicode(100))
  admin_loc = Column(Unicode(50))
  origin = Column(Unicode(100))
  orig_loc = Column(Unicode(50))
  lower_court = Column(Unicode(100))
  low_court_loc = Column(Unicode(50))
  low_court_disp = Column(Unicode(20))
  low_court_disp_dir = Column(Unicode(20))
  disposition = Column(Unicode(20))
  
  # Date Variables
  dec_date = Column(Date)
  granted_date = Column(Date)
  
  # Decision Variables
  dec_dir = Column(Unicode(20))
  dec_type = Column(Unicode(20))
  dec_unconst = Column(Boolean)
  prec_alt = Column(Boolean)
  per_curiam = Column(Boolean)
  
  # Text Variables
  syllabus = Column(UnicodeText)
  holding = Column(UnicodeText)
  facts = Column(UnicodeText)
  conclusion = Column(UnicodeText)
  questions = relationship('Question', back_populates='case')
  
  # Parties
  parties = relationship('Party', back_populates='case')
  petitioner = relationship('Petitioner', back_populates = 'case', uselist=False)
  respondent = relationship('Respondent', back_populates='case', uselist=False)
  amici = relationship('Amicus', back_populates='case')
  winning_side = Column(Unicode(20))
  
  # Vote Data
  votes = relationship('Vote', back_populates='case')
  justices = association_proxy('votes', 'justice')
  
  
  @property
  def winner(self):
    if self.winning_side == 'petitioner':
      return self.petitioner
    elif self.winning_side == 'respondent':
      return self.respondent
    else:
      return None
    
  def __repr__(self):
    return '<Case(docket={}, name={})>'.format(self.docket, self.name)
    
class Question(Base):
  __tablename__ = 'questions'
  case_id = Column(Integer, ForeignKey('cases.id'), nullable=False)
  case = relationship('Case', back_populates='questions')
  text = Column(UnicodeText)
  disposition = Column(Unicode(100))