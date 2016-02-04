from sqlalchemy import Column, Integer, String, Unicode, UnicodeText, Date, Boolean, Enum, ForeignKey
from sqlalchemy.orm import relationship
from base import Base

class Justice(Base):
  __tablename__ = 'justices'
  name = Column(Unicode(100), index=True, unique=True)
  cases = relationship('Vote', back_populates='justice')
  gender = Column(Unicode(1))
  # opinions_written =
  # opinions_joined = 
  
  @classmethod
  def by_name(cls, session):
    return dict([(name, id) for name, id in session.query(cls.name, cls.id)])

class Vote(Base):
  __tablename__ = 'votes'
  justice_id = Column(Integer, ForeignKey('justices.id'), nullable=False)
  case_id = Column(Integer, ForeignKey('cases.id'), nullable=False)
  is_clear = Column(Boolean, nullable=False)
  with_majority = Column(Boolean)
  direction = Column(Unicode(20))
  kind = Column(Unicode(100))
  justice = relationship('Justice', back_populates='cases')
  case = relationship('Case', back_populates='votes')
  
# class Opinion(Base):
  # __tablename__ = 'opinions'
  # case_id = Column(Integer, ForeignKey('case.id'), nullable=False)
  # authors
  # joiners
  # text
  # kind
  
  