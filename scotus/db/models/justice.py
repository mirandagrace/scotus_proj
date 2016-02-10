from sqlalchemy import Column, Integer, String, Unicode, UnicodeText, Date, Boolean, Enum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.hybrid import hybrid_property
from .base import Base

class Justice(Base):
  __tablename__ = 'justices'
  
  name = Column(Unicode(100), index=True, unique=True) # oyez
  oyez_id = Column(Integer, index=True, unique=True) # oyez
  gender = Column(Unicode(1)) # oyez
  date_start = Column(Date) # oyez
  date_end = Column(Date) # oyez
  appointed_by = Column(Unicode(100)) # oyez
  
  votes = relationship('Vote', back_populates='justice')
  cases = association_proxy('votes', 'case')
  
  opinion_associations = relationship('OpinionAssociation', back_populates='justice')
  opinions = association_proxy('opinion_associations', 'opinion')
  
  opinions_written = relationship('OpinionWritten', back_populates='justice')
  authored = association_proxy('opinion_written', 'opinion')
  
  opinions_joined = relationship('OpinionJoined', back_populates='justice')
  joined = association_proxy('opinion_associations', 'opinion')
  
  @classmethod
  def by_name(cls, session):
    return dict([(name, id) for name, id in session.query(cls.name, cls.id)])

class Vote(Base):
  __tablename__ = 'votes'
  
  is_clear = Column(Boolean, nullable=False) # scdb
  vote = Column(Unicode(20)) # scdb oyez
  direction = Column(Unicode(20)) # scdb
  
  justice_id = Column(Integer, ForeignKey('justices.id'), nullable=False)
  justice = relationship('Justice', back_populates='votes')
  
  case_id = Column(Integer, ForeignKey('cases.id'), nullable=False)
  case = relationship('Case', back_populates='votes')
  
  @property
  def side(self):
    if self.case.winning_side == None:
      return None
    if self.vote == 'majority':
      return self.case.winning_side
    if self.vote == 'minority':
      return self.case.losing_side
  
class OpinionAssociation(Base):
  __tablename__ = 'opinionassociation'
  kind = Column(Unicode(20))
  
  opinion_id = Column(Integer, ForeignKey('opinions.id'), nullable=False)
  opinion = relationship('Opinion', back_populates='justices_associated')
  
  justice_id = Column(Integer, ForeignKey('justices.id'), nullable=False)
  justice = relationship('Justice', back_populates='opinion_associations')
  
  __mapper_args__ = {'polymorphic_on': kind}
  
class OpinionWritten(OpinionAssociation):
  __mapper_args__ = {'polymorphic_identity': 'wrote'}
  
class OpinionJoined(OpinionAssociation):
  __mapper_args__ = {'polymorphic_identity': 'joined'}
  
class Opinion(Base):
  __tablename__ = 'opinions'
  
  kind = Column(Unicode(20), nullable=False) # oyez casetext
  type = Column(Unicode(20), nullable=False) # oyez casetext
  text = Column(UnicodeText) # casetext
  
  justices_associated = relationship('OpinionAssociation', back_populates='opinion')
  justices = association_proxy('justices_associated', 'justice')
  
  justices_writing = relationship('OpinionWritten', back_populates='opinion')
  authors = association_proxy('justices_writing', 'justice')
  
  justices_joining = relationship('OpinionJoined', back_populates='opinion')
  joiners = association_proxy('justices_joining', 'justice')
  
  case_id = Column(Integer, ForeignKey('cases.id'), nullable=False)
  case = relationship('Case', back_populates='opinions')
  
  __mapper_args__ = {'polymorphic_on': type}
  
class Dissent(Opinion):
  __mapper_args__ = {'polymorphic_identity': 'dissent'}
  
class Judgement(Opinion):
  __mapper_args__ = {'polymorphic_identity': 'judgement'}
  
class Concurrence(Opinion):
  __mapper_args__ = {'polymorphic_identity': 'concurrence'}
  
# dissent
# holding:
# per curiam
# majority
# plurality
# concurrence
# special concurrence
  