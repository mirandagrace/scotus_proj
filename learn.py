from scotus.db import DB
from scotus.settings import DEFAULT_DB
from scotus.learn import vote_predict
import pandas as pd
import numpy as np
import sklearn 
from sklearn.preprocessing import LabelEncoder, OneHotEncoder, StandardScaler
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD, PCA
from sklearn.base import BaseEstimator, TransformerMixin
import matplotlib.pyplot as plt
from sklearn_pandas import DataFrameMapper, cross_val_score
from sklearn.pipeline import Pipeline, FeatureUnion

def justice_data(justice_id, data):
  return data[data['justice_id']==justice_id]
  
class DocumentList(BaseEstimator, TransformerMixin):
  def __init__(self, column_id=None):
    self.column_id = column_id
    
  def fit(self, X, y=None):
    return self
  
  def transform(self, X, y=None):
    return X[self.column_id].tolist()
  
def text_extractor(column):
  return Pipeline([('extract', DocumentList(column_id=column)),
                   ('tfidf', TfidfVectorizer()),
                   ('lsa', TruncatedSVD())])
                   

y_mapper = DataFrameMapper([('vote', LabelEncoder())])

statistics = DataFrameMapper([
                ('gender_petitioner', LabelEncoder()),
                ('gender_respondent', LabelEncoder()),
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

features = FeatureUnion([
            ('facts', text_extractor('facts')),
            ('document_petitioner', text_extractor('document_petitioner')),
            ('document_respondent', text_extractor('document_respondent')),
            ('justice_document_petitioner', text_extractor('justice_document_petitioner')),
            ('justice_document_respondent', text_extractor('justice_document_respondent')),
            ('statistics', statistics)])

db = DB(DEFAULT_DB)
data = vote_predict.fetch_data(db)

justice_data = justice_data(4, data)

case_names = justice_data['name']

vote_predict = Pipeline([
                  ('features', features),
                  ('scale', StandardScaler()),
                  ('pca', PCA())])

X = vote_predict.fit_transform(justice_data)
y = y_mapper.fit_transform(justice_data)
      
plt.scatter(X[:, 0], X[:, 1], c=y.flatten(), cmap='bwr')                



                