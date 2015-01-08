#!/usr/bin/env python
import sys
from twython import Twython
from twython import TwythonStreamer
from textblob import TextBlob
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.externals import joblib
from sklearn import svm

# your twitter consumer and access information
apiKey = 'bGM1BfpCh5d9UpsXFSAlvSRjE'
apiSecret = 'SquBbg9kQ1Zz6YxmNG2vJwlnoL8zinLdXEgdanFb4686KOmPms'
accessToken = '2959173920-PvIHay0j4KQicFml2MQXV2ZfDnWR1qbea55Qr0H'
accessTokenSecret = 'Ky2XMQ46rZ6jj97O3PHYCL5RIAixRc0JQEWsufn1S7mA1'

# sentiment analysis model
txt2vec = joblib.load('saved_model/vectorizer.pickel')
model = joblib.load('saved_model/svm_model.pk1')


# post a tweet to @plant_jones
def sendTweet(tweetStr):
   api = Twython(apiKey,apiSecret,accessToken,accessTokenSecret)
   api.update_status(status=tweetStr)
   print "Tweeted: " + tweetStr

# class to handle streaming random tweets
class MyStreamer(TwythonStreamer):
    
    #    def __init__(self, **kwargs):
    #    txt2vec = joblib.load('saved_model/vectorizer.pickel')
    #    model = joblib.load('saved_model/svm_model.pk1')

    def on_success(self, data):
        if 'text' in data:
            ascii_tweet = data['text']
            utf_tweet = ascii_tweet.encode('utf-8')
            model.predict(txt2vec.transform([str(utf_tweet)])) 
            # estimate the sentiment of the tweet
        #    blob = TextBlob(ascii_tweet)
        #    polarity = str(blob.polarity)

            print (utf_tweet + '\t' + polarity + '\n')
            # Want to disconnect after the first result?
            # self.disconnect()

    def on_error(self, status_code, data):
        print status_code, data
       

# grab a random tweet
def randomTweetFromStream():
    stream = MyStreamer(apiKey,apiSecret,accessToken,accessTokenSecret)
    stream.statuses.filter(track='water', language='en')



if __name__ == "__main__":

#    if len(sys.argv) < 2:
#        print ("Must supply tweet string")
#        sys.exit()
#
#    tweetStr = sys.argv[1]
#    sendTweet(tweetStr)

    randomTweetFromStream()
