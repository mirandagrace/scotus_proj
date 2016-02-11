from scotus.db.build import Build
from scotus.db.add import *
from scotus.db import DB
from scotus.config import TEST_DB
from utilities import *


def name_collision():
  build = Build()
  phase_1 = build.add(0, add_justices)
  phase_2 = build.add(1, add_justices)
  return

def test_no_duplication():
  db = DB(TEST_DB)
  db.reset()
  build = Build()
  phase_1 = build.add(0, add_justices)
  db.populate(build)
  db.populate(build)
  return

def test_name_collision():
  assert raises(name_collision, ValueError)