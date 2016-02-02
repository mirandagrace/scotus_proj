from sqlalchemy import Column, Integer, String, Unicode, UnicodeText, Date, Boolean
from base import Base

# class containing the information about the individual case
class Case(Base):
  __tablename__ = 'cases'
  
  # Identification Variables
  scdb_id = Column(Unicode(20), nullable=False, unique=True, index=True)
  citation = Column(Unicode(100))
  docket = Column(Unicode(20), nullable=False, index=True)
  name = Column(Unicode(100))
  
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
  
  # Date Variables
  dec_date = Column(Date)
  granted_date = Column(Date)
  
  # Decision Variables
  dec_dir = Column(Unicode(20))
  dec_type = Column(Unicode(20))
  dec_unconst = Column(Boolean, nullable=False)
  prec_alt = Column(Boolean, nullable=False)
  per_curiam = Column(Boolean, nullable=True)
  
  # Text Variables
  syllabus = Column(UnicodeText)
  holding = Column(UnicodeText)
  facts = Column(UnicodeText)
  conclusion = Column(UnicodeText)