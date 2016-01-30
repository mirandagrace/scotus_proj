from sqlalchemy import Column

class Base(object):
    id =  Column(Integer, primary_key=True, autoincrement=True)

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base(cls=Base)