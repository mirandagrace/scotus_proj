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
    turn_query = select([Turn, Advocacy.side, Argument.date, Argument.case_id,
                         Advocate.gender]).where(and_(Section.id == Turn.section_id, 
                                 Advocacy.id == Section.advocacy_id,
                                 Advocate.id == Advocacy.advocate_id,
                                 Argument.id == Section.argument_id))
    
    turn_data = sql.read_sql_query(turn_query, con=db.engine, index_col='id',
                                   parse_dates=['date'])
    turn_data.drop(['section_id', 'advocate_id'], inplace=True, axis=1)
    turn_data.columns = ['kind', 'turn_number', 'text', 'time_start', 'time_end',
                         'justice_id', 'side', 'date', 'case_id', 'gender']    
    turn_data['length'] = np.abs(turn_data['time_end'] - turn_data['time_start'])
    turn_data.drop(['time_start', 'time_end', 'turn_number'], inplace=True, axis=1)
    turn_data['interrupted'] = turn_data['text'].str.endswith('--')
    turn_data['interruption'] = turn_data['interrupted'].shift(1).fillna(False)
    turn_data['gender'] = turn_data['gender'].apply(gender_encode)
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
        'document': [group['text'].str.cat( )],
        'name': [group['name'].min()]})

def justice_names(db):
    session = db.Session()
    try:
        d = Justice.by_name(session)
        session.commit()
    except:
        session.rollback()
        raise
    justice_data = []
    for name, id in d.iteritems():
        justice_data.append({'id':id, 'name':name.lower().strip(' jr.').split()[-1]})
    return pandas.DataFrame.from_records(justice_data, index='id')

def case_justice_features(data):
    data.drop(['kind', 'date'], axis=1, inplace=True)
    case_side_groups = data.groupby(['case_id', 'justice_id', 'side'])
    features = case_side_groups.apply(justice_agg).unstack('side')
    features.columns = ['justice_'+'_'.join(col).strip() for col in features.columns.values]
    features.drop(['justice_name_petitioner'], axis=1, inplace=True)
    features.reset_index(inplace=True)
    features.drop(['level_2'], inplace=True, axis=1)
    features.rename(columns={'justice_name_respondent':'justice_name'}, inplace=True)
    return features
    
def case_transcript_features(data):
    data.drop(['kind', 'justice_id'], axis=1, inplace=True)
    case_side_groups = data.groupby(['case_id', 'side'])
    features = case_side_groups.apply(case_agg).fillna(value={'document':'', 'gender':'M'}).fillna(value=0).unstack(u'side')
    features.columns = ['_'.join(col).strip() for col in features.columns.values]
    features.reset_index(inplace=True)
    features.drop(['date_petitioner', 'level_1'], inplace=True, axis=1)
    features.rename(columns={u'date_respondent':'date_argued', 'dec_date': 'date_decided'}, inplace=True)
    features.set_index('case_id', inplace=True)
    return features
    
def get_case_data(db):
    return sql.read_sql_query(select([Case.name, 
                                      Case.winning_side,
                                      Case.facts,
                                      Case.dec_date,
                                      Case.dec_type,
                                      Case.id]), con=db.engine, index_col='id',
                                      parse_dates=['dec_date'])
                                      
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
        
def fetch_data(db):
    transcript_data = get_transcript_data(db)
    case_data = transcript_data.copy()[transcript_data.kind != 'justice']
    case_features = case_transcript_features(case_data)
    names = justice_names(db)
    justice_data = transcript_data.copy()[transcript_data.kind == 'justice'].join(names, on='justice_id', how='left')
    justice_features = case_justice_features(justice_data)
    justice_features.fillna(value={'justice_document_petitioner':'', 
                                   'justice_document_respondent':''}, inplace=True)
    justice_features.fillna(value=0, inplace=True)
    justice_features = justice_features
    case_data = get_case_data(db)
    case_data = case_data.join(case_features)
    vote_data = get_vote_data(db)
    vote_case_data = vote_data.join(case_data, on='case_id', how='left')
    justice_vote_case_data = pandas.merge(vote_case_data, justice_features,
                             on=['justice_id', 'case_id'], how='left')
    justice_vote_case_data.loc[(justice_vote_case_data['vote'] == 'none') & (justice_vote_case_data['dec_type'] == 'per curiam'), 'vote'] = u'majority'
    votes = justice_vote_case_data[['vote', 'case_id']].groupby(['case_id'],  as_index=False).agg(lambda x: len(x[x['vote']=='majority']))
    votes.rename(columns={'vote':'majority'}, inplace=True)
    justice_vote_case_data = pandas.merge(justice_vote_case_data, votes, on=['case_id'], how='left')
    justice_vote_case_data['vote'] = justice_vote_case_data.apply(get_vote_side, axis = 1)
    justice_vote_case_data.rename(columns={'dec_date': 'date_decided'}, inplace=True)
    justice_vote_case_data.drop(['case_id', 'winning_side'], inplace=True, axis=1)
    justice_vote_case_data.dropna(subset=['facts', 'majority', 'document_petitioner', 'date_argued', 'document_respondent'],
                                  inplace=True)
    justice_vote_case_data.fillna(value={'justice_document_petitioner':'', 
                                   'justice_document_respondent':''}, inplace=True)
    justice_vote_case_data.fillna(value=0, inplace=True)                           
    return justice_vote_case_data
    