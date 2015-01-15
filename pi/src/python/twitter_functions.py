#!/usr/bin/env python
import sys

from twython import Twython
from twython import TwythonStreamer

# sys.path.insert(0, '/home/pv/plant_jones_root/plant_jones/sentiment_analysis')
from sentiment_analysis.sentiment_analysis_model import load_serial, create_vectors

# your twitter consumer and access information
apiKey = 'bGM1BfpCh5d9UpsXFSAlvSRjE'
apiSecret = 'SquBbg9kQ1Zz6YxmNG2vJwlnoL8zinLdXEgdanFb4686KOmPms'
accessToken = '2959173920-PvIHay0j4KQicFml2MQXV2ZfDnWR1qbea55Qr0H'
accessTokenSecret = 'Ky2XMQ46rZ6jj97O3PHYCL5RIAixRc0JQEWsufn1S7mA1'
saved_model_dir = 'saved_model/'

# post a tweet to @plant_jones
def sendTweet(tweetStr):
    api = Twython(apiKey, apiSecret, accessToken, accessTokenSecret)
    api.update_status(status=tweetStr)
    print "Tweeted: " + tweetStr


# class to handle streaming random tweets
class MyStreamer(TwythonStreamer):

    target_sentiment = "negative"
    model = None
    char_vectorizer = None
    word_vectorizer = None
    lexicons = None

    def initialize(self, target_sentiment):
        MyStreamer.target_sentiment = "\""+target_sentiment+"\""
        # sentiment analysis model
        MyStreamer.model, MyStreamer.char_vectorizer, \
        MyStreamer.word_vectorizer, MyStreamer.lexicons = load_serial()

    def on_success(self, data):
        try:
            if 'text' in data:
                ascii_tweet = data['text']
                utf_tweet = ascii_tweet.encode('utf-8')
                vectors = create_vectors(
                    [utf_tweet], self.word_vectorizer, self.char_vectorizer, self.lexicons)
                tweet_sentiment = self.model.predict(vectors)[0]
                # estimate the sentiment of the tweet

                if tweet_sentiment == self.target_sentiment:
                    print (utf_tweet + '\t' + tweet_sentiment + '\n')
                    # sendTweet(utf_tweet)
                    # Want to disconnect after the first result?
                    # self.disconnect()
        except:
            pass

    def on_error(self, status_code, data):
        print status_code, data


# grab a random tweet
def randomTweetFromStream(target_sentiment):
    stream = MyStreamer(apiKey, apiSecret, accessToken, accessTokenSecret)
    stream.initialize(target_sentiment)
    stream.statuses.filter(track='water', language='en')


if __name__ == "__main__":
    sentiment = "negative" if sys.argv[1] == '0' else "positive"
    randomTweetFromStream(sentiment)
