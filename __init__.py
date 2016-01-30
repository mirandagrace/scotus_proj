from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DB = 'sqlite://data/scotus.db'

engine = create_engine(DB)

Session = sessionmaker(bind=engine)