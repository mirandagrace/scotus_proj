from scotus.db import DB
from scotus.settings import DEFAULT_DB
import pandas
from pandas.io import sql
from scotus.db.models import *

db = DB(DEFAULT_DB)

session = db.Session()

unknown_turn_data = sql.read_sql_query(session.query(Turn).filter(kind=u'unknown').statement, 
                                       con=db.engine)
print turn_data.columns.values