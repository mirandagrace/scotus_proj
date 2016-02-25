from scotus.db import DB
from scotus.settings import DEFAULT_DB
import pandas

db = DB(DEFAULT_DB)

session = db.Session()

