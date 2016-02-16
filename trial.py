import sys
import argparse
from scotus.db import DB
from scotus.db.models import *
from scotus.build import Build
from scotus.settings import TEST_DB, DEFAULT_DB, SCDB_TEST_FILE, SCDB_VOTES_FILE
from scotus.add import add_justices, add_scdb_votes

def build_db(db_file, data_file):

  build = Build()
  phase_1 = build.add(0, add_justices)
  phase_2 = build.add(1, lambda x: add_scdb_votes(x, scdb_f=data_file), name='add_scdb_votes')

  db = DB(db_file)
  db.reset()

  db.populate(build)
  
  session = db.Session()
  return

if __name__=='__main__':
  parser = argparse.ArgumentParser('Build the database.')
  parser.add_argument('-t', '--test', action='store_true', help='run in the test environment')
  args = parser.parse_args()
  if args.test:
    build_db(TEST_DB, SCDB_TEST_FILE)
  else:
    build_db(DEFAULT_DB, SCDB_VOTES_FILE)
  