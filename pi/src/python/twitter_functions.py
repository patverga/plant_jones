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

# sentiment analysis model
model, char_vectorizer, word_vectorizer, lexicons = load_serial()

# post a tweet to @plant_jones
def sendTweet(tweetStr):
    api = Twython(apiKey, apiSecret, accessToken, accessTokenSecret)
    api.update_status(status=tweetStr)
    print "Tweeted: " + tweetStr


# class to handle streaming random tweets
class MyStreamer(TwythonStreamer):

    target_sentiment = "negative"

    def set_sentiment(self, target_sentiment):
        MyStreamer.target_sentiment = "\""+target_sentiment+"\""

    def on_success(self, data):
        if 'text' in data:
            ascii_tweet = data['text']
            utf_tweet = ascii_tweet.encode('utf-8')
            vectors = create_vectors([utf_tweet], word_vectorizer, char_vectorizer, lexicons)
            tweet_sentiment = model.predict(vectors)[0]
            # estimate the sentiment of the tweet

            if tweet_sentiment == self.target_sentiment:
                print (utf_tweet + '\t' + tweet_sentiment + '\n')
                # sendTweet(utf_tweet)
                # Want to disconnect after the first result?
                # self.disconnect()

    def on_error(self, status_code, data):
        print status_code, data


# grab a random tweet
def randomTweetFromStream(target_sentiment):
    stream = MyStreamer(apiKey, apiSecret, accessToken, accessTokenSecret)
    stream.set_sentiment(target_sentiment)
    stream.statuses.filter(track='water', language='en')


if __name__ == "__main__":
    sentiment = "negative" if sys.argv[1] == 0 else "positive"
    randomTweetFromStream(sentiment)
