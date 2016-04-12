from transformers import *
from scipy import interp
from sklearn.metrics import roc_curve, auc, classification_report, accuracy_score
from sklearn.naive_bayes import MultinomialNB
from sklearn.learning_curve import validation_curve
from sklearn.cross_validation import KFold,  StratifiedKFold, StratifiedShuffleSplit, ShuffleSplit
from sklearn.pipeline import Pipeline, FeatureUnion
import matplotlib.pyplot as plt
%matplotlib inline

def cv_roc(prediction, df, y, test_size=50, n_iter=3, years=None):
    #w = weights.values.flatten().astype(float)/9.0
    mean_tpr = 0.0
    mean_fpr = np.linspace(0, 1, 100)
    all_tpr = []
    scores = []
    cv = StratifiedShuffleSplit(y, n_iter=n_iter, test_size=test_size)
    #years = years
   # for i, year in enumerate(years):
    for i, (train, test) in enumerate(cv):
        #train = df['year'].values<year
       # test = df['year'].values==year
        try:
           trn = df.iloc[train]
           tst = df.iloc[test]
        except:
            trn = df[train]
            tst = df[test]
        prediction.fit(trn, y[train])
        probas_ = prediction.predict_proba(tst)
        classes_ = prediction.predict(tst)
        #classes_ = 2*classes_-1
        # Compute ROC curve and area the curve
        fpr, tpr, thresholds = roc_curve(y[test], probas_[:, 1])
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
        scores.append(accuracy_score(y[test], classes_)-accuracy_score(y[test], [-1]*len(y[test])))
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
    plt.title('Receiver operating characteristic example')
    plt.legend(loc="lower right")
    plt.show()
    print np.mean(scores)
    return

def nb_model(feature_list, text, count):
    text_features = FeatureUnion([(col, NamedTfidfVectorizer([('feature', Document(columns=col)),
                                                            ('tfidf', TfidfVectorizer(min_df=2,
                                                                                      max_df=1.0,
                                                                                      norm=None,
                                                                                      use_idf=False,
                                                                                      token_pattern = ur"(?u)\b[A-Za-z]\w\w+\b",
                                                                                      ngram_range=(1,1)))]))
                                 for col in text if 'thomas' not in col])

    fact_features = NamedTfidfVectorizer([('feature', Document(columns='facts')),
                                          ('tfidf', TfidfVectorizer(min_df=2,
                                                                    max_df=1.0,
                                                                    norm=None,
                                                                    use_idf=False,
                                                                    token_pattern = ur"(?u)\b[A-Za-z]\w\w+\b",
                                                                    ngram_range=(1,1)))]))

    speaker_features = NamedTfidfVectorizer([('feature', Document(columns='speaker')),
                                             ('tfidf', TfidfVectorizer(min_df=2,
                                                                      max_df=1.0,
                                                                      norm=None,
                                                                      use_idf=False,
                                                                      ngram_range=(4,4))]))

    stat_features =  NamedFeature(columns=count)

    feature_dict = {'questions':text_features, 'counts':stat_features, 'facts':fact_features, 'speaker':speaker_features}

    all_features = FeatureUnion([x in feature_dict.iteritems() if x[0] in feature_list])

    model = Pipeline([('data', all_features),
                      ('select', GenericUnivariateSelect(mode='fpr', param=.05)),
                      ('predict', BaggingClassifier(MultinomialNB(),
                                                    n_estimators=25, 
                                                    max_samples=.9, 
                                                    max_features=.9, 
                                                    bootstrap=False, 
                                                   # bootstrap_features=True, 
                                                    oob_score=False, 
                                                    warm_start=False, 
                                                    n_jobs=1, 
                                                    random_state=None,
                                                    verbose=0))])
    return model