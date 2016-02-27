from scotus.db import DB
from scotus.settings import DEFAULT_DB
from scotus.vote_prediction.query import query
import pandas as pd
import numpy as np
import sklearn 
import sklearn.preprocessing
import sklearn.decomposition
from sklearn_pandas import DataFrameMapper, cross_val_score
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.feature_extraction.text import CountVectorizer

def justice_data(justice_id, data):
  return data[data['justice_id']==justice_id]
  
class DataFrameExtractor(DataFrameMapper):
  def __init__(self, columns):
    DataFrameMapper([(columns, None)])
  
def text_extractor_factory(column):
  return Pipeline([('extract', DataFrameMapper([(column, None)])),
                   ('tfidf', sklearn.preprocessing.TfidfVectorizer()),
                   ('lsa', sklearn.decomposition.TruncatedSVD())])

db = DB(DEFAULT_DB)
data = query(db)

justice_data = justice_data(4, data)

case_names = justice_data['names']

y_mapper = DataFrameMapper([('vote', sklearn.preprocessing.LabelEncoder())])

features = FeatureUnion

x_mapper = DataFrameMapper([
        ('facts', LSA()),
        ('document_petitioner', sklearn.preprocessing.TfidfVectorizer()),
        ('document_respondent', sklearn.preprocessing.TfidfVectorizer()),
        ('gender_petitioner', sklearn.preprocessing.OneHotEncoder()),
        ('gender_respondent', sklearn.preprocessing.OneHotEncoder()),
        ('interrupted_petitioner', None),
        ('interrupted_respondent', None),
        ('interrupting_petitioner', None),
        ('interrupting_respondent', None),
        ('number_turns_petitioner', None),
        ('number_turns_respondent', None),
        ('speaking_time_petitioner', None),
        ('speaking_time_respondent', None),
        ('turn_length_petitioner', None),
        ('turn_length_respondent', None),
        ('justice_document_petitioner', sklearn.preprocessing.TfidfVectorizer()),
        ('justice_document_respondent', sklearn.preprocessing.TfidfVectorizer()),
        ('justice_interrupted_petitioner', None),
        ('justice_interrupted_respondent', None),
        ('justice_interrupting_petitioner', None),
        ('justice_interrupting_respondent', None),
        ('justice_number_turns_petitioner', None),
        ('justice_number_turns_respondent', None),
        ('justice_speaking_time_petitioner', None),
        ('justice_speaking_time_respondent', None),
        ('justice_turn_length_petitioner', None),
        ('justice_turn_length_respondent', None),
        ])