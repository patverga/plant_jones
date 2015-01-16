# #!/usr/bin/env python
import sys
import socket
import csv
from twython import Twython
from twython import TwythonStreamer
# sys.path.insert(0, '/home/pemma/plant_jones/pi/src/python/sentiment_analysis')
from sentiment_analysis.sentiment_analysis_model import load_serial, create_vectors

# read in secret keys -> create a csv with your twitter secret keys
secret_key_file = ".secret_keys"
with open(secret_key_file, 'r') as f:
    keys = {type: key for (type, key) in csv.reader(f, delimiter=',')}

# sentiment analysis model
saved_model_dir = 'saved_model/'
model, char_vectorizer, word_vectorizer, lexicons = load_serial()

# post a tweet to @plant_jones
def sendTweet(tweetStr):
    api = Twython(keys['apiKey'], keys['apiSecret'], keys['accessToken'], keys['accessTokenSecret'])
    api.update_status(status=tweetStr)
    print "Tweeted: " + tweetStr


# class to handle streaming random tweets
class MyStreamer(TwythonStreamer):
    target_sentiment = '\"negative\"'

    def initialize(self, target_sentiment):
        print("Looking for tweets with " + target_sentiment + " sentiment")
        MyStreamer.target_sentiment = "\""+target_sentiment+"\""

    def on_success(self, data):
        try:
            if 'text' in data:
                ascii_tweet = data['text']
                utf_tweet = ascii_tweet.encode('utf-8')
                vectors = create_vectors(
                    [utf_tweet], word_vectorizer, char_vectorizer, lexicons)
                tweet_sentiment = str(model.predict(vectors)[0])
                # estimate the sentiment of the tweet

                if tweet_sentiment == self.target_sentiment:
                    print (utf_tweet + '\t' + tweet_sentiment + '\n')
                    sendTweet(utf_tweet)
                    # Want to disconnect after the first result?
                    self.disconnect()
        except:
            pass

    def on_error(self, status_code, data):
        print status_code, data


# grab a random tweet
def randomTweetFromStream(sentiment_code):
    target_sentiment = 'positive' if sentiment_code == "1" else 'negative'
    stream = MyStreamer(keys['apiKey'], keys['apiSecret'], keys['accessToken'], keys['accessTokenSecret'])
    stream.initialize(target_sentiment)
    stream.statuses.filter(track='water', language='en')


# set up server
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ('localhost', 10000)
print >> sys.stderr, 'starting up on %s port %s' % server_address
sock.bind(server_address)

# Listen for incoming connections
sock.listen(1)
while True:
    # Wait for a connection
    print >> sys.stderr, 'waiting for a connection'
    connection, client_address = sock.accept()
    try:
        print >> sys.stderr, 'connection from', client_address
        # Receive the data in small chunks and retransmit it
        while True:
            data = connection.recv(16)
            if not data:
                break
            print >> sys.stderr, 'received "%s"' % data
            randomTweetFromStream(data)
    finally:
        # Clean up the connection
        connection.close()
