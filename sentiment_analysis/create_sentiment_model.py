import csv
import gzip

import nltk
import numpy as np
import scipy.sparse as sp
import itertools

from numpy import array
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.cross_validation import cross_val_score
from sklearn.externals import joblib
from sklearn.grid_search import GridSearchCV
from sklearn.metrics import classification_report
from sklearn.svm import SVC

lexicon_root = '/home/pv/plant_jones_root/plant_jones/sentiment_analysis/lexicons/combined/'
train_data_file = 'tweets-b-train'
test_data_file = 'dev-tweets-b'
saved_model_dir = 'saved_model/'


def create_vectors(data, word_vectorizer, char_vectorizer, lexicons):
    #### NGram features ####
    print "Getting ngram features"
    word_vectors = word_vectorizer.transform(data)
    char_vectors = char_vectorizer.transform(data)

    #### lexicon features ####
    tokenized_data = map(nltk.word_tokenize, data)
    unigram_dict, bigram_dict, pair_dict, pair_unigram_set = lexicons

    # convert each tweet to a list of sentiment scores based on tokens / bigrams / and skipgrams
    print "Creating lexicon features."
    unigram_token_scores = [[unigram_dict.get(token) for token in tokens if token in unigram_dict] for tokens in
                            tokenized_data]
    bigram_data = [[' '.join(bigram) for bigram in nltk.bigrams(tokens)] for tokens in tokenized_data]
    bigram_token_scores = [[bigram_dict.get(bigram) for bigram in bigrams if bigram in bigram_dict] for bigrams in
                           bigram_data]
    pair_unigrams_data = [[token for token in tokens if token in pair_unigram_set] for tokens in tokenized_data]
    pair_token_scores = [
        [pair_dict.get(' '.join(sorted(pair))) for pair in itertools.combinations(pair_unigrams, r=2) if
         ' '.join(sorted(pair)) in pair_dict] for pair_unigrams in pair_unigrams_data]

    # get the various features form the scores
    lexicon_vectors = np.hstack([extract_lexicon_scores(unigram_token_scores),
                                 extract_lexicon_scores(bigram_token_scores),
                                 extract_lexicon_scores(pair_token_scores)])

    # combine all the features into a single matrix
    # Note: when combining numpy array and sparse scipy, must use scipy.sparse.hstack
    return sp.hstack([word_vectors, char_vectors, lexicon_vectors])


# TODO remove redundant iterations
def extract_lexicon_scores(token_scores):
    # sum of term scores
    total_score = array([sum(scores) for scores in token_scores])
    # max term score
    max_score = array([max(scores) if len(scores) > 0 else 0 for scores in token_scores])
    # take only positive scores for next two measures
    positive_scores = [[score for score in scores if (score > 0)] for scores in token_scores]
    # count of positive scores
    positive_count = array([len(scores) for scores in positive_scores])
    # score of the last positive term
    last_positive = array([scores[-1] if len(scores) > 0 else 0 for scores in positive_scores])
    return array([total_score, max_score, positive_count, last_positive]).T


def train_model(data, labels, save=True):
    word_vectorizer = CountVectorizer(min_df=1, encoding='utf8', ngram_range=(1, 4), analyzer='word')
    char_vectorizer = CountVectorizer(min_df=1, encoding='utf8', ngram_range=(1, 5), analyzer='char')
    word_vectorizer.fit(data)
    char_vectorizer.fit(data)

    lexicons = create_lexicons()
    train_dat = create_vectors(data, word_vectorizer, char_vectorizer, lexicons)
    train_lab = array(labels)

    print('Fitting model.')
    model = SVC(gamma=0.0001, C=100)
    # print(cross_val_score(model, train_dat, train_lab, scoring='f1'))
    model.fit(train_dat, train_lab)

    if save:
        save_serial(model, char_vectorizer, word_vectorizer, lexicons)

    return model, char_vectorizer, word_vectorizer, lexicons


def test_model(test_data, test_labels, model, char_vectorizer, word_vectorizer, lexicons):
    print ('Testing model.')
    X_test = create_vectors(test_data, word_vectorizer, char_vectorizer, lexicons)
    y_test = array(test_labels)
    y_true, y_pred = y_test, model.predict(X_test)
    print(classification_report(y_true, y_pred))


def tune_model(train_data, train_labels):
    tuned_parameters = [{'kernel': ['rbf'], 'gamma': [1e-3, 1e-4],
                         'C': [1, 10, 100, 1000]},
                        {'kernel': ['linear'], 'C': [1, 10, 100, 1000]}]
    model = GridSearchCV(SVC(C=1), tuned_parameters, cv=5, scoring='f1', n_jobs=-1)
    X_test = create_vectors(train_data, word_vectorizer, char_vectorizer, lexicons)
    y_test = array(train_labels)

    print('Tuning hyperparams')
    model.fit(X_test, y_test)
    print(model.best_params_)


def load_serial():
    print 'Deserializing learned model, vectorizers, and lexicons'
    char_vectorizer = joblib.load(saved_model_dir + 'char_vectorizer.pickle')
    word_vectorizer = joblib.load(saved_model_dir + 'word_vectorizer.pickle')
    model = joblib.load(saved_model_dir + 'svm_model.pk1')
    lexicons = joblib.load(saved_model_dir + 'lexicons.pickle')
    return model, char_vectorizer, word_vectorizer, lexicons


def save_serial(model, char_vectorizer, word_vectorizer, lexicons):
    print 'Serializing learned model, vectorizers, and lexicons'
    joblib.dump(model, saved_model_dir + 'svm_model.pk1')
    joblib.dump(word_vectorizer, saved_model_dir + 'word_vectorizer.pickle')
    joblib.dump(char_vectorizer, saved_model_dir + 'char_vectorizer.pickle')
    joblib.dump(lexicons, saved_model_dir + 'lexicons.pickle')


def create_lexicons():
    print ('Loading Lexicons')
    unigram_dict = {}
    with gzip.open(lexicon_root + 'unigrams.gz', 'r') as uni_file:
        for line in uni_file:
            token, score = line.split('\t')
            unigram_dict[token] = float(score)

    bigram_dict = {}
    with gzip.open(lexicon_root + 'bigrams.gz', 'r') as bi_file:
        for line in bi_file:
            token, score = line.split('\t')
            bigram_dict[token] = float(score)

    pair_dict = {}
    pair_unigram_set = set()
    with gzip.open(lexicon_root + 'pairs.gz', 'r') as pair_file:
        for line in pair_file:
            token, score = line.split('\t')
            pair_tokens = sorted(token.split('---'))
            pair_unigram_set.add(pair_tokens[0])
            pair_unigram_set.add(pair_tokens[1])
            pair_dict[' '.join(pair_tokens)] = float(score)

    return unigram_dict, bigram_dict, pair_dict, pair_unigram_set


print ('Loading data')
with open(train_data_file, 'r') as f:
    train_data, train_labels = zip(*[(row[3], row[2]) for row in csv.reader(f, delimiter='\t', quotechar='|')])
with open(test_data_file, 'r') as f:
    test_data, test_labels = zip(*[(row[3], row[2]) for row in csv.reader(f, delimiter='\t', quotechar='|')])

# tune model
# model, char_vectorizer, word_vectorizer, lexicons = load_serial()
# tune_model(train_data, train_labels)

# # train model
model, char_vectorizer, word_vectorizer, lexicons = train_model(train_data, train_labels, True)

# # test model
test_model(test_data, test_labels, model, char_vectorizer, word_vectorizer, lexicons)