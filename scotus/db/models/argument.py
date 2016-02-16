from sqlalchemy import Column, Integer, String, Unicode, UnicodeText, Date, Boolean, Enum, ForeignKey, String, Float
from sqlalchemy.orm import relationship
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.hybrid import hybrid_property
from .base import Base

class Advocate(Base):
  __tablename__ = 'advocates'
  name = Column(Unicode(150)) # oyez
  oyez_id = Column(Integer, index=True) # oyez
  gender = Column(Unicode(1)) # calculated
  case_advocacies = relationship('Advocacy', back_populates='advocate')
  cases = association_proxy('case_advocacies', 'case')

class Advocacy(Base):
  __tablename__ = 'advocacies'
  side = Column(Unicode(15))

  case_id = Column(Integer, ForeignKey('cases.id'), nullable=False)
  case = relationship('Case', back_populates='case_advocacies')

  advocate_id = Column(Integer, ForeignKey('advocates.id'), nullable=False)
  advocate = relationship('Advocate', back_populates='case_advocacies')

class Argument(Base):
  __tablename__ = 'arguments'
  date = Column(Date)
  oyez_id = Column(Integer, index=True)

  case_id = Column(Integer, ForeignKey('cases.id'), nullable=False)
  case = relationship('Case', back_populates='arguments')

  sections = relationship('Section', back_populates='argument')

class Section(Base):
  __tablename__ = 'sections'

  number = Column(Integer, nullable=False)

  argument_id = Column(Integer, ForeignKey('arguments.id'), nullable=False)
  argument = relationship('Argument', back_populates='sections')

  advocacy_id = Column(Integer, ForeignKey('advocacies.id'), nullable=False)
  advocacy = relationship('Advocacy')
  advocate = association_proxy('advocacy', 'advocate')

  turns = relationship('Turn', back_populates='section')

class Turn(Base):
  __tablename__ = 'turns'

  kind = Column(Unicode(15))
  number = Column(Integer, nullable=False)

  sections_id = Column(Integer, ForeignKey('sections.id'), nullable=False)
  section = relationship('Section', back_populates='turns')

  text = Column(UnicodeText, nullable=False)

  time_start = Column(Float)
  time_end = Column(Float)

  __mapper_args__ = {'polymorphic_on': kind}

  @hybrid_property
  def length(self):
      return self.time_start - self.time_end

  @property
  def speaker(self):
    return None

class AdvocateTurn(Turn):
  advocate = association_proxy('section', 'advocate')

  @property
  def speaker(self):
    return self.advocate

  __mapper_args__ = {'polymorphic_identity': 'advocate'}

class JusticeTurn(Turn):
  @declared_attr
  def justice_id(cls):
      "Start date column, if not present already."
      return Turn.__table__.c.get('justice_id', Column(Integer, ForeignKey('justices.id'), nullable=False))

  justice = relationship('Justice')

  @property
  def speaker(self):
    return self.justice

  __mapper_args__ = {'polymorphic_identity': 'justice'}


