from transformers import *
from sklearn.cluster import KMeans
import numpy as np

def lsa_model():
  return ReductionPipeline([('feature', Document(columns='facts')),
                            ('count', TfidfVectorizer(min_df= 3, 
                                                      max_df=.95,
                                                      sublinear_tf=True,
                                                      stop_words='english',
                                                      token_pattern = ur"(?u)\b[A-Za-z]\w\w+\b",
                                                      ngram_range=(1,2))),
                            ('reduce', TruncatedSVD(n_components=100))])

def word_cloud(model, x, n_words):
    scores = model.get_params()['reduce'].components_[x]
    mrank = np.argsort(scores)
    prank = np.argsort(-1*scores)
    words = model.get_params()['count'].get_feature_names()
    mwords = np.array([words[r] for r in mrank])
    pwords = np.array([words[r] for r in prank])
    print 'PLUS: ' + '|'.join(pwords[:n_words]) + '\n\nMINUS: ' + '|'.join(mwords[:n_words])
    return