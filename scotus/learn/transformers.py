from sklearn.feature_extraction.text import TfidfVectorizer, TfidfTransformer, CountVectorizer
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.decomposition import LatentDirichletAllocation, TruncatedSVD
from sklearn.pipeline import Pipeline, FeatureUnion
    
class NamedFeature(BaseEstimator, TransformerMixin):
    
    def __init__(self, columns=None):
        self.columns = columns
         
    def get_feature_names(self):
        return self.columns
    
    def fit(self, X, y=None):
        return self
  
    def transform(self, X, y=None):
        return X[self.columns].values 
    
class Document(NamedFeature, TransformerMixin):
    def fit(self, X, y=None):
        return self
    
    def transform(self, X, y=None):
        return X[self.columns].tolist()
    
class ReductionPipeline(Pipeline):
    def make_topic_desc(self, topic_row):
        rank = np.argsort(topic_row)
        words = self.get_params()['count'].get_feature_names()
        try:
            support = self.get_params()['select'].get_support()
            words = np.extract(support, words)
        except KeyError:
            pass
        return '|'.join(np.extract(rank>len(words)-5, words)).replace(' ', '_') \
               + '\n' + '|'.join(np.extract(rank<5, words)).replace(' ', '_')
    
    def get_feature_names(self):
        try:
            coeffs = self.get_params()['reduce'].components_
            return np.apply_along_axis(self.make_topic_desc, 1, coeffs)
        except:
            words = self.get_params()['count'].get_feature_names()
            try:
                support = self.get_params()['select'].get_support()
                words = np.extract(support, words)
            except KeyError:
                pass
            return words
    
    def plot(self):
        plt.plot(range(0,len(self.get_params()['reduce'].explained_variance_)), 
                 self.get_params()['reduce'].explained_variance_)
        
        