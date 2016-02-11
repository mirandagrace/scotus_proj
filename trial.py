from scotus.db import DB, Build
from scotus.config import TEST_DB
from scotus.db.add import add_justices, add_scdb_votes

build = Build()
phase_1 = build.add(0, add_justices)
phase_2 = build.add(1, add_scdb_votes)

db = DB(TEST_DB)
db.reset()

db.populate(build)