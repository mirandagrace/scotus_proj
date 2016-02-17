from sqlalchemy import Column, Integer, String, Unicode, UnicodeText, Date, Boolean, Enum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import bindparam
from .base import Base, bakery
from .case import Case

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
  authored = association_proxy('opinions_written', 'opinion')
  
  opinions_joined = relationship('OpinionJoined', back_populates='justice')
  joined = association_proxy('opinion_associations', 'opinion')
  
  @classmethod
  def by_name(cls, session):
    return dict([(name, id) for name, id in session.query(cls.name, cls.id)])

  @classmethod
  def search_by_oyez_id(cls, session, oyez_id):
    baked_query = bakery(lambda session: session.query(cls))
    baked_query += lambda q: q.filter(cls.oyez_id == bindparam('oyez_id'))
    result = baked_query(session).params(oyez_id=oyez_id).one_or_none()
    return result

class Vote(Base):
  __tablename__ = 'votes'
  
  is_clear = Column(Boolean) # scdb
  vote = Column(Unicode(20)) # scdb oyez
  direction = Column(Unicode(20)) # scdb
  
  justice_id = Column(Integer, ForeignKey('justices.id'), nullable=False)
  justice = relationship('Justice', back_populates='votes', uselist=False)
  
  case_id = Column(Integer, ForeignKey('cases.id'), nullable=False)
  case = relationship('Case', back_populates='votes', uselist=False)
  
  @property
  def side(self):
    if self.case.winning_side == None:
      return None
    if self.vote == 'majority':
      return self.case.winning_side
    if self.vote == 'minority':
      return self.case.losing_side

  @classmethod
  def search_for_scraped(cls, session, justice_oyez_id, case_oyez_id):
    baked_query = bakery(lambda session: session.query(cls).join(Case, cls.case).join(Justice, cls.justice))
    baked_query += lambda q: q.filter(Case.oyez_id == bindparam('case_oyez_id'),
                                      Justice.oyez_id == bindparam('justice_oyez_id'))
    result = baked_query(session).params(justice_oyez_id=justice_oyez_id, case_oyez_id=case_oyez_id).one_or_none()
    return result
  
class OpinionAssociation(Base):
  __tablename__ = 'opinionassociation'
  kind = Column(Unicode(20))
  
  opinion_id = Column(Integer, ForeignKey('opinions.id'), nullable=False)
  opinion = relationship('Opinion', back_populates='justices_associated')
  
  justice_id = Column(Integer, ForeignKey('justices.id'), nullable=False)
  justice = relationship('Justice', back_populates='opinion_associations')
  
  __mapper_args__ = {'polymorphic_on': kind}
  
class OpinionWritten(OpinionAssociation):
  __mapper_args__ = {'polymorphic_identity': u'wrote'}
  
class OpinionJoined(OpinionAssociation):
  __mapper_args__ = {'polymorphic_identity': u'joined'}
  
class Opinion(Base):
  __tablename__ = 'opinions'
  
  kind = Column(Unicode(20)) # oyez casetext
  opinion_type = Column(Unicode(20))
  text = Column(UnicodeText) # casetext
  
  justices_associated = relationship('OpinionAssociation', back_populates='opinion', cascade="all, delete-orphan")
  justices = association_proxy('justices_associated', 'justice')
  
  justices_writing = relationship('OpinionWritten', back_populates='opinion', cascade="all, delete-orphan")
  authors = association_proxy('justices_writing', 'justice')
  
  justices_joining = relationship('OpinionJoined', back_populates='opinion', cascade="all, delete-orphan")
  joiners = association_proxy('justices_joining', 'justice')
  
  case_id = Column(Integer, ForeignKey('cases.id'), nullable=False)
  case = relationship('Case', back_populates='opinions')
  
  __mapper_args__ = {'polymorphic_on': kind}

  @classmethod
  def search_by_author_vote(cls, session, case_id, author_id):
    baked_query = bakery(lambda session: session.query(cls).join(OpinionWritten, cls.justices_writing))
    baked_query += lambda q: q.filter(Case.id == bindparam('case_id'),
                                      OpinionWritten.justice_id == bindparam('justice_id'))
    result = baked_query(session).params(justice_id=author_id, case_id=case_id).one_or_none()
    return result
  
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
  