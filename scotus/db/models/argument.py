from sqlalchemy import Column, Integer, String, Unicode, UnicodeText, Date, Boolean, Enum, ForeignKey, String, Float
from sqlalchemy.orm import relationship
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import bindparam
from .base import Base, bakery, OyezIdMixin

class Advocate(Base, OyezIdMixin):
  __tablename__ = 'advocates'
  name = Column(Unicode(150)) # oyez
  gender = Column(Unicode(1)) # calculated
  advocacies = relationship('Advocacy', back_populates='advocate')
  cases = association_proxy('advocacies', 'case')

  def __repr__(self): #pragma: no cover
    return '<Advocate(name={})>'.format(self.name)

  @classmethod
  def search_by_oyez_id(cls, session, oyez_id=None):
    baked_query = bakery(lambda session: session.query(cls))
    baked_query += lambda q: q.filter(cls.oyez_id == bindparam('oyez_id'))
    result = baked_query(session).params(oyez_id=oyez_id).one_or_none()
    return result

  @classmethod
  def search_for_scraped(cls, session, oyez_id=None):
    baked_query = bakery(lambda session: session.query(cls))
    baked_query += lambda q: q.filter(cls.oyez_id == bindparam('oyez_id'))
    result = baked_query(session).params(oyez_id=oyez_id).one_or_none()
    return result

class Advocacy(Base):
  __tablename__ = 'advocacies'
  side = Column(Unicode(15))
  role = Column(Unicode(50))

  case_id = Column(Integer, ForeignKey('cases.id'), nullable=False)
  case = relationship('Case', back_populates='advocacies')

  advocate_id = Column(Integer, ForeignKey('advocates.id'))
  advocate = relationship('Advocate', back_populates='advocacies')
  
  def __repr__(self): #pragma: no cover
    return '<Advocacy({}, {}, role={})>'.format(self.case, self.advocate, self.role)

  @classmethod
  def search_for_scraped(cls, session, case_id, advocate_oyez_id):
    baked_query = bakery(lambda session: session.query(cls).join(Advocate, cls.advocate))
    baked_query += lambda q: q.filter(cls.case_id == bindparam('case_id'))
    baked_query += lambda q: q.filter(Advocate.oyez_id == bindparam('advocate_oyez_id'))
    result = baked_query(session).params(case_id=case_id, advocate_oyez_id=advocate_oyez_id).one_or_none()
    return result

class Argument(Base, OyezIdMixin):
  __tablename__ = 'arguments'
  date = Column(Date)
  case_id = Column(Integer, ForeignKey('cases.id'), nullable=False)
  
  case = relationship('Case', back_populates='arguments')

  sections = relationship('Section', back_populates='argument')
  
  def __repr__(self): #pragma: no cover
    return '<Argument({}, date={})>'.format(self.case, self.date)

  @classmethod
  def search_by_oyez_id(cls, session, oyez_id=None):
    baked_query = bakery(lambda session: session.query(cls))
    baked_query += lambda q: q.filter(cls.oyez_id == bindparam('oyez_id'))
    result = baked_query(session).params(oyez_id=oyez_id).one_or_none()
    return result
  
  @classmethod
  def search_for_scraped(cls, session, oyez_id=None):
    baked_query = bakery(lambda session: session.query(cls))
    baked_query += lambda q: q.filter(cls.oyez_id == bindparam('oyez_id'))
    result = baked_query(session).params(oyez_id=oyez_id).one_or_none()
    return result

class Section(Base):
  __tablename__ = 'sections'

  number = Column(Integer, nullable=False)

  argument_id = Column(Integer, ForeignKey('arguments.id'), nullable=False)
  argument = relationship('Argument', back_populates='sections')

  advocacy_id = Column(Integer, ForeignKey('advocacies.id'))
  advocacy = relationship('Advocacy')
  advocate = association_proxy('advocacy', 'advocate')
  side = association_proxy('advocacy', 'side')

  turns = relationship('Turn', back_populates='section')

  @classmethod
  def search_for_scraped(cls, session, argument_oyez_id=None, number=None):
    baked_query = bakery(lambda session: session.query(cls).join(Argument, cls.argument))
    baked_query += lambda q: q.filter(Argument.oyez_id == bindparam('argument_oyez_id'))
    baked_query += lambda q: q.filter(cls.number == bindparam('number'))
    result = baked_query(session).params(argument_oyez_id=argument_oyez_id, number=number).one_or_none()
    return result

class Turn(Base):
  __tablename__ = 'turns'

  kind = Column(Unicode(15))
  number = Column(Integer, nullable=False)

  section_id = Column(Integer, ForeignKey('sections.id'), nullable=False)
  section = relationship('Section', back_populates='turns')

  text = Column(UnicodeText, nullable=False)

  time_start = Column(Float)
  time_end = Column(Float)

  __mapper_args__ = {'polymorphic_on': kind, 'polymorphic_identity': u'unknown'}

  @hybrid_property
  def length(self):
      return self.time_start - self.time_end

  @property
  def speaker(self):
    return None

  @staticmethod
  def search_for_scraped(session, argument_oyez_id=None, section_number=None, number=None):
    baked_query = bakery(lambda session: session.query(Turn).join(Section, Turn.section).join(Argument, Section.argument))
    baked_query += lambda q: q.filter(Argument.oyez_id == bindparam('argument_oyez_id'))
    baked_query += lambda q: q.filter(Section.number == bindparam('section_number'))
    baked_query += lambda q: q.filter(Turn.number == bindparam('number'))
    result = baked_query(session).params(argument_oyez_id=argument_oyez_id, section_number=section_number, number=number).one_or_none()
    return result
    
class AdvocateTurn(Turn):
  @declared_attr
  def advocate_id(cls):
    return Turn.__table__.c.get('advocate_id', Column(Integer, ForeignKey('advocates.id')))

  advocate = relationship('Advocate')
    
  @property
  def speaker(self):
    return self.advocate

  __mapper_args__ = {'polymorphic_identity': u'advocate'}

class JusticeTurn(Turn):
  @declared_attr
  def justice_id(cls):
    return Turn.__table__.c.get('justice_id', Column(Integer, ForeignKey('justices.id')))

  justice = relationship('Justice')

  @property
  def speaker(self):
    return self.justice
    
  __mapper_args__ = {'polymorphic_identity': u'justice'}


