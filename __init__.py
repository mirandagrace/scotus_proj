from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DB = 'sqlite:///scotus.db'

engine = create_engine(DB)

Session = sessionmaker(bind=engine)