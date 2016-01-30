import csv
from scotus_proj import Session

SCDB_ISSUE_FILE = 'data/scdb/SCDB_2015_01_caseCentered_LegalProvision.csv'
SCDB_CASE_FILE = 'data/scdb/SCDB_2015_01_caseCentered_Citation.csv'
SCDB_VOTE_FILE = 'data/scdb/SCDB_2015_01_justiceCentered_Citation.csv'

def add_case(case_row):
  # TODO: Process case, send to database.
  return  

def add_cases():
  # open the csv file
  with open(SCDB_CASE_FILE, 'r') as csvfile:
    reader = csv.DictReader(csvfile)
    # iterate through the cases, adding as you go
    for case in read:
      add_case(case)
  return

# main function that builds the database
def main():
  session = Session()
  # start with the reading in just the case data
  add_cases()
  # TODO: add vote data
  # TODO: add issue tagging 
  return
        
if __name__ == "__main__":
    main()