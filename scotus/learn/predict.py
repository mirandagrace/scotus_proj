from transformers import *
from transformers import NamedTfidfVectorizer
from scipy import interp
from sklearn.feature_selection import f_classif, chi2, GenericUnivariateSelect
from sklearn.ensemble import BaggingClassifier
from sklearn.linear_model import SGDClassifier
from sklearn.metrics import roc_curve, auc, classification_report, accuracy_score, matthews_corrcoef, log_loss, make_scorer, roc_auc_score
from sklearn.naive_bayes import MultinomialNB
from sklearn.learning_curve import validation_curve
from sklearn.cross_validation import KFold,  StratifiedKFold, StratifiedShuffleSplit, ShuffleSplit
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.preprocessing import PolynomialFeatures
from sklearn.grid_search import RandomizedSearchCV
import scipy.stats as ss
import matplotlib.pyplot as plt
import numpy as np


def cv_roc(prediction, df, y, test_size=50, n_iter=3, years=None, name='', kfold=False):
    #w = weights.values.flatten().astype(float)/9.0
    mean_tpr = 0.0
    mean_fpr = np.linspace(0, 1, 100)
    all_tpr = []
    scores = []
    mscores = []
    lscores = []
    if not kfold:
        cv = StratifiedShuffleSplit(y, n_iter=n_iter, test_size=test_size)
    else:
        cv = StratifiedKFold(y, n_iter, shuffle=True)
    #years = years
   # for i, year in enumerate(years):
    for i, (train, test) in enumerate(cv):
        #train = df['year'].values<year
       # test = df['year'].values==year
        try:
           trn = df.iloc[train]
           tst = df.iloc[test]
           y_trn = y.iloc[train]
           y_tst = y.iloc[test]
        except:
            trn = df[train]
            tst = df[test]
            y_trn = y[train]
            y_tst = y[test]
        prediction.fit(trn, y_trn)
        probas_ = prediction.predict_proba(tst)
        classes_ = prediction.predict(tst)
        #classes_ = 2*classes_-1
        # Compute ROC curve and area the curve
        fpr, tpr, thresholds = roc_curve(y_tst, probas_[:, 1])
        mean_tpr += interp(mean_fpr, fpr, tpr)
        mean_tpr[0] = 0.0
        roc_auc = auc(fpr, tpr, reorder=True)
        try:
            plt.plot(fpr, tpr, lw=1, label='ROC fold %d (area = %0.2f)' % (i, roc_auc))
        except:
            plt.plot(fpr, tpr, lw=1, label='ROC fold %d (area = %0.2f)' % (i, roc_auc))
        #print classification_report(y[test], classes_)
        #print accuracy_score(y[test], classes_)
        #print accuracy_score(y[test], classes_)-accuracy_score(y[test], [-1]*len(y[test]))
        scores.append(accuracy_score(y_tst, classes_))
        mscores.append(matthews_corrcoef(y_tst, classes_))
        lscores.append(log_loss(y_tst, probas_))
    try:
        plt.plot([0, 1], [0, 1], '--', color=(0.6, 0.6, 0.6), label='Luck')
    except:
        plt.plot([0, 1], [0, 1], '--', color=(0.6, 0.6, 0.6), label='Luck')
   # mean_tpr /= len(years)
    mean_tpr /= len(cv)
    mean_tpr[-1] = 1.0
    mean_auc = auc(mean_fpr, mean_tpr)
    plt.plot(mean_fpr, mean_tpr, 'k--',
             label='Mean ROC (area = %0.2f)' % mean_auc, lw=2)

    plt.xlim([-0.05, 1.05])
    plt.ylim([-0.05, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('Receiver operating characteristic {}'.format(name))
    plt.legend(loc="lower right")
    plt.show()
    print 'Accuracy: {}'.format(np.mean(scores))
    print 'Normalized Accuracy: {}'.format(np.mean(scores)-.6)
    print 'Matthews: {}'.format(np.mean(mscores))
    print 'Cross-Entropy: {}'.format(np.mean(lscores))
    return

def test_roc(prediction, X, y, name=''):
    probas_ = prediction.predict_proba(X)
    classes_ = prediction.predict(X)
    fpr, tpr, thresholds = roc_curve(y, probas_[:, 1])
    roc_auc = auc(fpr, tpr, reorder=True)
    plt.plot(fpr, tpr, lw=1, label='area = %0.2f' % (roc_auc))
    print classification_report(y, classes_)
    print 'Accuracy: {}'.format(accuracy_score(y, classes_))
    print 'Normalized Accuracy: {}'.format(accuracy_score(y, classes_)-.6)
    print 'Matthews: {}'.format(matthews_corrcoef(y, classes_))
    try:
        plt.plot([0, 1], [0, 1], '--', color=(0.6, 0.6, 0.6), label='Luck')
    except:
        plt.plot([0, 1], [0, 1], '--', color=(0.6, 0.6, 0.6), label='Luck')
    plt.xlim([-0.05, 1.05])
    plt.ylim([-0.05, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('Receiver operating characteristic {}'.format(name))
    plt.legend(loc="lower right")
    plt.show()
    return

def grid_search(model, X, y, params, n_iter=5, scoring=make_scorer(matthews_corrcoef), verbose=0, error_score=0, n_jobs=1):
    g = RandomizedSearchCV(model, params, n_iter=n_iter, scoring=scoring, 
                           error_score=0, verbose=verbose, n_jobs=n_jobs, cv=StratifiedKFold(y, n_folds=3, shuffle=True))
    g.fit(X, y)
    return g

def nb_model(feature_list, text, count, names):
    text_features = [(col, NamedTfidfVectorizer([('feature', Document(columns=col)),
                                                            ('tfidf', TfidfVectorizer(min_df=3,
                                                                                      max_df=1.9,
                                                                                      norm=None,
                                                                                      use_idf=False,
                                                                                      token_pattern = ur"(?u)\b[A-Za-z]\w\w+\b",
                                                                                      ngram_range=(1,1)))]))
                                 for col in text if (('thomas' not in col) and (col.split('_')[1] in names or 'advocate' in col))]

    advocate_features = [(col, NamedTfidfVectorizer([('feature', Document(columns=col)),
                                                    ('tfidf', TfidfVectorizer(min_df=3,
                                                                              max_df=.9,
                                                                              norm=None,
                                                                             # use_idf=False,
                                                                              token_pattern = ur"(?u)\b[A-Za-z]\w\w+\b",
                                                                              ngram_range=(1,1)))]))
                         for col in ['text_advocate_petitioner', 'text_advocate_respondent']]

    fact_features = [('facts', NamedTfidfVectorizer([('feature', Document(columns='facts')),
                                          ('tfidf', TfidfVectorizer(min_df=3,
                                                                    max_df=.9,
                                                                    norm=None,
                                                                    use_idf=False,
                                                                    token_pattern = ur"(?u)\b[A-Za-z]\w\w+\b",
                                                                    ngram_range=(1,1)))]))]

    speaker_features = [('speaking_order', NamedTfidfVectorizer([('feature', Document(columns='speaking_order')),
                                             ('tfidf', TfidfVectorizer(min_df=3,
                                                                       max_df=.9,
                                                                       norm=None,
                                                                       use_idf=False,
                                                                       ngram_range=(3,3)))]))]

    stat_features =  [('stats', NamedFeature(columns=count))]

    feature_dict = {'questions':text_features, 'counts':stat_features, 'facts':fact_features, 'speaker':speaker_features}

    in_use = []
    for name, feature in feature_dict.iteritems():
        if name in feature_list:
            in_use += feature

    all_features = FeatureUnion(in_use)

    model = Pipeline([('data', all_features),
                      ('select', GenericUnivariateSelect(score_func=chi2, mode='fpr', param=.000001)),
                      ('predict', BaggingClassifier(MultinomialNB(),
                                                    n_estimators=10, 
                                                    max_samples=.95, 
                                                    max_features=10, 
                                                    bootstrap=False, 
                                                    bootstrap_features=False))])
    return model

def nb_params(text, names):
    tfidf_base_params = [('__tfidf__min_df', [2, 3]), 
                         ('__tfidf__max_df', ss.uniform(.8, .2)),
                         ('__tfidf__use_idf', [True, False]),
                         #('__tfidf__ngram_range', [(1,1), (2,2), (3,3)],
                        # ('__tfidf__norm', ['l1', None]),
                         ]

    params = {}
    for x in text:
        for param, dist in tfidf_base_params:
            if (('thomas' not in x) and ((x.split('_')[1] in names))):
               params['data__'+x+param] = dist

    for x in ['speaking_order']:#, 'text_advocate_petitioner', 'text_advocate_respondent']:
        for param, dist in tfidf_base_params:
            params['data__'+x+param] = dist

    params.update({'select__param': ss.uniform(0.05, .25)})

    params.update({#'predict__n_estimators':[5,10],
                   'predict__max_samples':ss.uniform(.8, .2),
                   'predict__max_features':ss.uniform(.5, .5)})

    return params

def lr_params(text, names):
    tfidf_base_params = [#('__tfidf__min_df', [2, 3]), 
                         #('__tfidf__max_df', ss.uniform(.8, .2)),
                         #('__tfidf__use_idf', [True, False]),
                         #('__tfidf__ngram_range', [(1,1), (2,2), (3,3)],
                         #('__tfidf__norm', ['l1', None]),
                         ]
    for x in text:
        for param, dist in tfidf_base_params:
            if (('thomas' not in x) and ((x.split('_')[1] in names))):
               params['data__'+x+param] = dist

    for x in ['facts', 'speaking_order', 'text_advocate_petitioner', 'text_advocate_respondent']:
        for param, dist in tfidf_base_params:
             params['data__'+x+param] = dist

    params = {}
    #params.update({'select__param': ss.uniform(0.0, .1)})

    params.update({#'predict__base_estimator__loss':['log', 'hinge'],
                   'predict__base_estimator__alpha':ss.uniform(0.05, .35)})

    #params.update({'predict__max_features':ss.uniform(0.5, .5)})

    return params




def lr_model(feature_list, text, count, length, names):
    text_features = [(col, NamedTfidfVectorizer([('feature', Document(columns=col)),
                                                            ('tfidf', TfidfVectorizer(min_df=3,
                                                                                      max_df=1.0,
                                                                                      norm=None,
                                                                                    #  use_idf=False,
                                                                                      token_pattern = ur"(?u)\b[A-Za-z]\w\w+\b",
                                                                                      ngram_range=(1,1)))]))
                                 for col in text if (('thomas' not in col) and (col.split('_')[1] in names))]

    advocate_features = [(col, NamedTfidfVectorizer([('feature', Document(columns=col)),
                                                        ('tfidf', TfidfVectorizer(min_df=3,
                                                                                  max_df=1.0,
                                                                                  norm=None,
                                                                                  #max_features=10000,
                                                                                 # use_idf=False,
                                                                                  token_pattern = ur"(?u)\b[A-Za-z]\w\w+\b",
                                                                                  ngram_range=(1,1)))]))
                             for col in ['text_advocate_petitioner', 'text_advocate_respondent']]

    fact_features = [('facts', NamedTfidfVectorizer([('feature', Document(columns='facts')),
                                          ('tfidf', TfidfVectorizer(min_df=3,
                                                                    max_df=1.0,
                                                                    norm=None,
                                                                    stop_words='english',
                                                                   # use_idf=False,
                                                                    token_pattern = ur"(?u)\b[A-Za-z]\w\w+\b",
                                                                    ngram_range=(1,1)))]))]

    speaker_features = [('speaking_order', NamedTfidfVectorizer([('feature', Document(columns='speaking_order')),
                                             ('tfidf', TfidfVectorizer(min_df=2,
                                                                       max_df=1.0,
                                                                       norm=None,
                                                                       #use_idf=False,
                                                                       ngram_range=(3,3)))]))]

    stat_features =  [('stats', NamedFeature(columns=count))]

    length_features =  [('length', NamedFeature(columns=length))]

    feature_dict = {'questions':text_features, 'counts':stat_features, 'facts':fact_features, 'speaker':speaker_features, 
                    'length':length_features, 'advocate':advocate_features}

    in_use = []
    for name, feature in feature_dict.iteritems():
        if name in feature_list:
            in_use += feature

    all_features = FeatureUnion(in_use)

    model = Pipeline([('data', all_features),
                      #('select', GenericUnivariateSelect(mode='fpr', param=.05)),
                      ('predict', BaggingClassifier(SGDClassifier(loss='log', 
                                                                  penalty='l1', 
                                                                  alpha=0.1),
                                                    n_estimators=40, 
                                                    max_samples=1.0, 
                                                    max_features=.8, 
                                                    bootstrap=True,
                                                    bootstrap_features=False))])
    return model