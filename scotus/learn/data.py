from scotus.db import DB
from scotus.settings import DEFAULT_DB
from sqlalchemy.sql import select, and_
from pandas.io import sql
from scotus.db.models import *
import numpy as np
import pandas
 
def gender_encode(x):
  if x != u"F":
    return 1
  else:
    return 0
 
def get_transcript_data(db):
    turn_query = select([Turn, Advocacy.side, Argument.date,
                         Argument.case_id]).where(and_(Section.id == Turn.section_id,
                                 Advocacy.id == Section.advocacy_id,
                                 Advocate.id == Advocacy.advocate_id,
                                 Argument.id == Section.argument_id))
   
    turn_data = sql.read_sql_query(turn_query, con=db.engine, index_col='id')
                                   #parse_dates=['date'])
    turn_data.drop(['section_id', 'advocate_id'], inplace=True, axis=1)
    turn_data.columns = ['kind', 'turn_number', 'text', 'time_start', 'time_end',
                         'justice_id', 'side', 'date', 'case_id']   
    turn_data['length'] = np.abs(turn_data['time_end'] - turn_data['time_start'])
    turn_data.drop(['time_start', 'time_end', 'turn_number'], inplace=True, axis=1)
    turn_data['interrupted'] = turn_data['text'].str.endswith('--').astype(int)
    turn_data['interruption'] = turn_data['interrupted'].shift(1).fillna(False)
    #turn_data['gender'] = turn_data['gender'].apply(gender_encode)
    turn_data['choppiness'] = (turn_data['text'].str.count('--')>1).astype(int)
    turn_data['humor'] = turn_data['text'].str.contains(r'\[Laughter\]').astype(int)
    turn_data['question'] = turn_data['text'].str.contains(r'[?]').astype(int)
    return turn_data
   
def case_agg(group):
    return pandas.DataFrame({
        'date': [group['date'].min()],
        'number_turns': [len(group['text'])],
        'gender': [group['gender'].max()],
        'turn_length': [group['length'].mean()],
        'speaking_time': [group['length'].sum()],
        'interrupting': [group['interruption'].sum()],
        'interrupted': [group['interrupted'].sum()],
        'document': [group['text'].str.cat(sep=' ')]})
        
def justice_agg(group):
    return pandas.DataFrame({
        'number_turns': [len(group['text'])],
        'turn_length': [group['length'].mean()],
        'speaking_time': [group['length'].sum()],
        'interrupting': [group['interruption'].sum()],
        'interrupted': [group['interrupted'].sum()],
        'document': [group['text'].str.cat( )]})
 
def case_justice_features(data):
    data.drop(['kind', 'date'], axis=1, inplace=True)
    case_side_groups = data.groupby(['case_id', 'justice_id', 'side'])
    features = case_side_groups.apply(justice_agg).unstack('side')
    features.columns = ['justice_'+'_'.join(col).strip() for col in features.columns.values]
    features.reset_index(inplace=True)
    try:
      features.drop(['level_2'], inplace=True, axis=1)
    except ValueError:
      pass
    return features
   
def case_transcript_features(data):
    data.drop(['kind', 'justice_id'], axis=1, inplace=True)
    case_side_groups = data.groupby(['case_id', 'side'])
    features = case_side_groups.apply(case_agg).fillna(value={'document':'', 'gender':'M'}).fillna(value=0)
    print features.columns.values
    features.drop(['level_2'], inplace=True, axis=1)
    features = features.pivot('case_id', 'side')
    features.columns = ['_'.join(col).strip() for col in features.columns.values]
    features.drop(['date_petitioner'], inplace=True, axis=1)
    features.rename(columns={u'date_respondent':'date_argued', 'dec_date': 'date_decided'}, inplace=True)
    return features
   
def get_case_data(db):
    return sql.read_sql_query(select([Case.name,
                                      Case.winning_side,
                                      Case.facts,
                                      Case.dec_type,
                                      Case.dec_date,
                                      Case.id,
                                      Case.scdb_id]), con=db.engine, index_col='id')
                                      #parse_dates=['dec_date'])
                                     
def get_vote_data(db):
    return sql.read_sql_query(select([Vote.id, Vote.vote, Vote.justice_id, Vote.case_id]),
                              con=db.engine, index_col='id')
 
def get_vote_side(x):
    vote = x['vote']
    winning_side = x['winning_side']
    if vote == 'majority':
        if winning_side == 'petitioner':
            return 'petitioner'
        elif winning_side == 'respondent':
            return 'respondent'
    elif vote == 'minority':
        if winning_side == 'petitioner':   
            return 'respondent'
        elif winning_side == 'respondent':
            return 'petitioner'
    else:
        return
       
def get_vote_side_numeric(x):
    vote = x['vote']
    winning_side = x['winning_side']
    if vote == 'majority':
        if winning_side == 'petitioner':
            return -1
        elif winning_side == 'respondent':
            return 1
    elif vote == 'minority':
        if winning_side == 'petitioner':   
            return 1
        elif winning_side == 'respondent':
            return -1
    else:
        return
       
def j_gender(id, axis=None):
  return id in [1, 2, 6, 11]

def term(d):
    try:
      y = d.year
      m = d.month
      if m > 8:
          return y
      else:
          return y-1
    except:
      return np.nan
   
def reshape(X, groups=[], aggregators={}, stack=None, drop=None, rename=None):
  dataframe = X.groupby(groups).agg(aggregators)
  if rename:
      dataframe.rename(columns=self.rename, inplace=True)
  if stack:
      for column in stack:
          dataframe = dataframe.unstack(column)
      dataframe.columns = ['_'.join(col).strip() for col in dataframe.columns.values]
  if drop:
      try:
          dataframe.drop(drop, inplace=True, axis=1)
      except:
          print dataframe.columns.values
          raise
  return dataframe

def lines_data():
  db = DB(DEFAULT_DB)
  #data = fetch_data(db) 
  transcript_data = get_transcript_data(db)
  case_data = get_case_data(db)
  vote_data = get_vote_data(db)
  session = db.Session()
  try:
    names = Justice.by_name(session).iteritems()
    justice_name = [{'id': id,
                     'speaker':name.rstrip('I').lower().split(',')[0].split()[-1]} for name, id in names]
  except:
    raise
  finally:
    session.close()
  name_data = pandas.DataFrame.from_records(justice_name, index='id')
  data = pandas.merge(vote_data, transcript_data, on=['case_id', 'justice_id'], how='outer').join(name_data, on='justice_id', how='left')
  data = data.join(case_data, on=['case_id'], how='left')
  #data.loc[data['justice_id'].apply(j_gender, axis=1) , 'gender'] = '0'
  data.loc[data['kind']=='advocate', 'speaker'] = 'advocate'
  data.rename(columns={'dec_date': 'date_decided',
                       'date':'date_argued',
                       'dec_type':'decision_type',
                       'kind':'turns'}, inplace=True)
  data.loc[(data['vote'] != 'majority')& (data['vote'] != 'minority') & (data['decision_type'] == 'per curiam'), ('vote')] = u'majority'
  data['vote_side'] = data.apply(get_vote_side_numeric, axis=1)
  data.dropna(subset=['facts', 'speaker'], inplace=True)
  majority = data.groupby(['case_id', 'speaker'], as_index=False)['vote'].agg('first').groupby('case_id').agg(lambda x: len(x[x=='majority']))['vote']
  minority = data.groupby(['case_id', 'speaker'], as_index=False)['vote'].agg('first').groupby('case_id').agg(lambda x: len(x[x=='minority']))['vote']
 # data = data[(data['speaker'] == 'advocate') | ((data['justice_id'] < 11) & (data['justice_id'] != 8))] 
  cases = reshape(data,
                  groups=['case_id'],
                  aggregators={'facts': 'first',
                               'name':'first',
                               'winning_side': 'first',
                               'decision_type': 'first',
                               'date_decided': 'first',
                               'date_argued': 'first',
                               'speaker': lambda x: ' '.join(x)
                               })
  votes = reshape(data,
                  groups=['case_id', 'speaker'],
                  aggregators={'vote_side':'first'},
                  stack=['speaker'],
                  drop=['vote_side_advocate'])
  speakers = reshape(data,
                     groups=['case_id', 'side', 'speaker'],
                     aggregators={'turns':'count',
                                  'interrupted': 'sum',
                                  'interruption': 'sum',
                                  'length': 'sum',
                                  'humor': 'sum',
                                  'choppiness': 'sum',
                                  'question': 'sum',
                                  'text': lambda x: ' '.join(x)},
                    stack=['speaker', 'side'])
  data = cases.join([votes, speakers])
  data['majority'] = majority
  data['minority'] = minority
  data.dropna(subset=['date_argued'], inplace=True)
  data['term'] = data['date_decided'].apply(term)
  data.fillna(value={x:'' for x in data.columns.values if 'text' in x}, inplace=True)
  data.fillna(value={'facts':'', 'speaker':''}, inplace=True)
  data.fillna(0, inplace=True)
  return data