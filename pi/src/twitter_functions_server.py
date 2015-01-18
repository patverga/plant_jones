# #!/usr/bin/env python
import asyncore
import csv
import socket
import threading
import time

from twython import Twython
from twython import TwythonStreamer
from sentiment_analysis.sentiment_analysis_model import load_serial, create_vectors


# post a tweet to @plant_jones
def send_tweet(tweet_str):
    api = Twython(keys['apiKey'], keys['apiSecret'], keys['accessToken'], keys['accessTokenSecret'])
    api.update_status(status=tweet_str)
    print "Tweeted: " + tweet_str


def respond_to_mentions():
    twitter = Twython(keys['apiKey'], keys['apiSecret'], keys['accessToken'], keys['accessTokenSecret'])
    mentions = twitter.get_mentions_timeline()
    if mentions:
        # Remember the most recent tweet id, which will be the one at index zero.
        for mention in mentions:
            who = mention['user']['screen_name']
            text = mention['text']
            theId = mention['id_str']
            print(who, text, theId)


# grab a random tweet
def random_tweet_from_stream(sentiment_code):
    # initialize stream using secret keys
    stream = MyStreamer(keys['apiKey'], keys['apiSecret'], keys['accessToken'], keys['accessTokenSecret'])
    stream.target_sentiment = "\"" + ('positive' if sentiment_code == "1" else 'negative') + "\""
    print("Looking for tweets with " + stream.target_sentiment + " sentiment")
    # we only want english tweets that contain the word water
    stream.statuses.filter(track='water', language='en')


# class to handle streaming random tweets
class MyStreamer(TwythonStreamer):
    target_sentiment = '\"negative\"'

    def on_success(self, data):
        try:
            if 'text' in data:
                ascii_tweet = data['text']
                utf_tweet = ascii_tweet.encode('utf-8')
                vectors = create_vectors(
                    [utf_tweet], word_vectorizer, char_vectorizer, lexicons)
                # estimate the sentiment of the tweet
                tweet_sentiment = str(model.predict(vectors)[0])
                if tweet_sentiment == self.target_sentiment:
                    print (utf_tweet + '\t' + tweet_sentiment + '\n')
                    # send_tweet(utf_tweet)
                    # Want to disconnect after the first result?
                    self.disconnect()
        except:
            pass

    def on_error(self, status_code, data):
        print status_code, data


# message handle for the twitter server
class MessageHandler(asyncore.dispatcher_with_send):
    def handle_read(self):
        data = self.recv(8192)
        if data:
            print data
            random_tweet_from_stream(data)


# socket server
class TwitterServer(asyncore.dispatcher):
    def __init__(self, host, port):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind((host, port))
        self.listen(5)
        # run this in its own thread so socket is not blocking
        loop_thread = threading.Thread(target=asyncore.loop, name="Socket Server Loop")
        loop_thread.start()

    def handle_close(self):
        self.close()

    def handle_accept(self):
        pair = self.accept()
        if pair is not None:
            sock, addr = pair
            print 'Incoming connection from %s' % repr(addr)
            handler = MessageHandler(sock)


# main loop running the server
def mention_check_loop():
    # only check mentions after delay
    mention_check_delay = 30.0  # 1800.0 # 30 mins
    while True:
        print "Checking for mentions"
        respond_to_mentions()
        time.sleep(mention_check_delay)


## read in secret keys -> create a csv with your twitter secret keys
with open(".secret_keys", 'r') as f:
    keys = {key: value for (key, value) in csv.reader(f, delimiter=',')}

## sentiment analysis model
model, char_vectorizer, word_vectorizer, lexicons = load_serial()

## initialize the server
server = TwitterServer('localhost', 6969)
mention_check_loop()