from scotus.db import DB
from scotus.build import Build
from scotus.config import TEST_DB
from scotus.add import add_justices, add_scdb_votes

def build_db():

  build = Build()
  phase_1 = build.add(0, add_justices)
  phase_2 = build.add(1, add_scdb_votes)

  db = DB(TEST_DB)
  db.reset()

  db.populate(build)
  return

if __name__=='__main__':
  build_db()