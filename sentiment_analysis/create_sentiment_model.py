from __future__ import print_function

import csv
from sklearn.feature_extraction.text import CountVectorizer
from pprint import pprint
from time import time
import logging
from sklearn.externals import joblib
from sklearn import svm, cross_validation
from numpy import array

with open('all', 'r') as csvfile:
#    dat = [(row[0],row[3]) for row in csv.reader(csvfile, delimiter=',', quotechar='|')]
    data, labels = zip(*[(row[3],row[1]) for row in csv.reader(csvfile, delimiter=',', quotechar='|')])
    labels = array(labels)

#with open('test', 'r') as csvfile:
#    test = [(row[0],row[3]) for row in csv.reader(csvfile, delimiter=',', quotechar='|')]
#    test_data, test_label = zip(*train)


#with open('verify', 'r') as csvfile:
#    verify = [(row[0],row[3]) for row in csv.reader(csvfile, delimiter=',', quotechar='|')]
#    verify_data, verify_label = zip(*train)

train_break = 10000

# create feature vectorizer

vectorizer = CountVectorizer(min_df=1, encoding='utf8')#, ngram_range(1,1))
print('getting count vectors')
X = vectorizer.fit_transform(data[:train_break])
print(X.shape)


train_dat = X #X[:train_break,:]
train_lab = array(labels[:train_break])
#test_dat = X[train_break:,:]
#test_lab = labels[train_break:]

print (len(train_lab), train_dat.shape)
print('Training SVM')
model = svm.SVC(gamma=0.001, C=100.)
#cross_validation.cross_val_score(model, train_dat, train_lab, scoring='accuracy')
model.fit(train_dat, train_lab)

joblib.dump(model, 'saved_model/svm_model.pk1')
joblib.dump(vectorizer, 'saved_model/vectorizer.pickle')
