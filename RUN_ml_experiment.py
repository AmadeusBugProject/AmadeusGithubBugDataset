import nltk
import numpy
import pandas
from nltk.stem.snowball import SnowballStemmer
from sklearn import metrics
from sklearn.datasets import load_files
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.linear_model import SGDClassifier, LogisticRegression
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC

from githubanalysis.common.Logger import Logger
from mlClassifier import isof1

log = Logger(log_file='log.txt')
nltk.download('stopwords')
stemmer = SnowballStemmer("english", ignore_stopwords=True)


class StemmedCountVectorizer(CountVectorizer):
    def __init__(self, stemming=True, input='content', encoding='utf-8',
                 decode_error='strict', strip_accents=None,
                 lowercase=True, preprocessor=None, tokenizer=None,
                 stop_words=None, token_pattern=r"(?u)\b\w\w+\b",
                 ngram_range=(1, 1), analyzer='word',
                 max_df=1.0, min_df=1, max_features=None,
                 vocabulary=None, binary=False, dtype=numpy.int64):
        self.stemming = stemming
        super().__init__(input=input, encoding=encoding,
                         decode_error=decode_error, strip_accents=strip_accents,
                         lowercase=lowercase, preprocessor=preprocessor, tokenizer=tokenizer,
                         stop_words=stop_words, token_pattern=token_pattern,
                         ngram_range=ngram_range, analyzer=analyzer,
                         max_df=max_df, min_df=min_df, max_features=max_features,
                         vocabulary=vocabulary, binary=binary, dtype=dtype)

    def build_analyzer(self):
        if self.stemming:
            analyzer = super(StemmedCountVectorizer, self).build_analyzer()
            return lambda doc: ([stemmer.stem(w) for w in analyzer(doc)])
        else:
            return super(StemmedCountVectorizer, self).build_analyzer()


classifiers = {'MNB': MultinomialNB(fit_prior=False),
               'LSVC': LinearSVC(random_state=42),
               'SGDC': SGDClassifier(penalty='l2', random_state=42),
               'RFC': RandomForestClassifier(n_estimators=200, max_depth=3, random_state=42),
               'LRC': LogisticRegression(random_state=42)}

parameters = {'MNB': {
                        # 'clf__alpha': [0.1, 0.2, 0.4, 0.8, 1],
                        'clf__alpha': [0.4, 1],
                        'clf__fit_prior': (True, False)},
              'LSVC': {
                        'clf__loss': ('hinge', 'squared_hinge'),
                        # 'clf__C': [1, 10, 100, 500, 1000]},
                        'clf__C': [1]},
              'SGDC': {
                        # 'clf__alpha': [0.01, 0.001, 0.0001]},
                        'clf__alpha': [0.1, 0.01]},
              'RFC': {
                        'clf__criterion': ("gini", "entropy")},
              'LRC': {
                        'clf__solver': ['newton-cg', 'lbfgs', 'liblinear', 'sag', 'saga'],
                        # 'clf__C': [1, 2, 4, 8, 10]}}
                        'clf__C': [4, 6, 8, 10]}}


def main():
    for k in range(101, 110):
        log.s('at iteration: ' + str(k))
        df = kfold_for_all_classifiers()
        df.to_csv('mlClassifier/figures/ml_5_fold_cross_validation' + str(k) + '.csv')
        isof1.plot_isof1(df, str(k))


def kfold_for_all_classifiers():
    report_df = pandas.DataFrame()
    issue_data_folder = 'mlClassifier/data/bugreports/'
    dataset = load_files(issue_data_folder, shuffle=False)
    log.s("n_samples: %d" % len(dataset.data))

    # split the dataset in training and test set:
    docs_train, docs_test, y_train, y_test = train_test_split(dataset.data, dataset.target, test_size=0.20, random_state=None)
    target_names = dataset.target_names

    for cls_name, classifier in classifiers.items():
        log.s('at classifier: ' + cls_name)
        single_report = run_ml_magic(y_train, y_test, docs_train, docs_test, target_names, classifier, parameters[cls_name])
        report = pandas.DataFrame(single_report)
        report['classifier'] = cls_name
        report_df = report_df.append(report)
    return report_df


def run_ml_magic(y_train, y_test, docs_train, docs_test, target_names, classifier, additional_parameters):
    pipeline = Pipeline([('vect', StemmedCountVectorizer()),
                         ('tfidf', TfidfTransformer()),
                         ('clf', classifier)])

    parameters = {
        # 'vect__stop_words': [None, 'english'],
        'vect__stop_words': ['english'],
        #'vect__stemming': [True, False],
        'vect__stemming': [True],
        'vect__ngram_range': [(1, 1), (1, 2)],
        # 'tfidf__use_idf': (True, False),
        'tfidf__use_idf': [False],
    }

    parameters.update(additional_parameters)

    grid_search = GridSearchCV(pipeline, parameters, n_jobs=-1, cv=5)
    grid_search.fit(docs_train, y_train)

    n_candidates = len(grid_search.cv_results_['params'])
    for i in range(n_candidates):
        log.s(str(i) + 'params - %s; mean - %0.2f; std - %0.2f'
              % (grid_search.cv_results_['params'][i],
                 grid_search.cv_results_['mean_test_score'][i],
                 grid_search.cv_results_['std_test_score'][i]))
    log.s('Best:')
    log.s('index: ' + str(grid_search.best_index_))
    log.s('score: ' + str(grid_search.best_score_))
    log.s('params: ' + str(grid_search.best_params_))
    log.s('estimator: ' + str(grid_search.best_estimator_))

    y_predicted = grid_search.predict(docs_test)

    log.s(metrics.classification_report(y_test, y_predicted, target_names=target_names))

    report = {
              'precision macro average': [metrics.precision_score(y_test, y_predicted, average="macro")],
              'precision weighted average': [metrics.precision_score(y_test, y_predicted, average="weighted")],
              'recall macro average': [metrics.recall_score(y_test, y_predicted, average="macro")],
              'recall weighted average': [metrics.recall_score(y_test, y_predicted, average="weighted")],
              'accuracy': [metrics.accuracy_score(y_test, y_predicted)],
              'F1 macro average': [metrics.f1_score(y_test, y_predicted, average="macro")],
              'F1 weighted average': [metrics.f1_score(y_test, y_predicted, average="weighted")],
              'GS Best Params': [grid_search.best_params_]
              }

    return report


if __name__ == "__main__":
    main()


