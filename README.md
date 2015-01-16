# plant_jones

![This is me](https://pbs.twimg.com/profile_images/553022075774840832/MPafmt1D.jpeg)

Plant Jones is a semi-intelligent, non-autonomous plant. He is capable of measuring, analyzing, and alerting others to his own moisture needs. 

Plant Jones also possesses [not quite developed social skills](https://twitter.com/plant_jones). He is able to parse tweets from human users and determine their sentiment at a rate statistically significantly above random chance. He uses these analyzed tweets to transmit information about his thirst levels in the hopes of garnering pity and water. 

When too dry, Plant Jones scours twitter for negative tweets about water to display his sadness in a way relevant to his needs. When he is wattered, Plant Jones tweets a positive tweet about water signaling how happy he is.

Parts
----
- 1x Arduino Uno
- 1x Rasberry Pi Model B+
- 2x [nRf24L01+ Tranciever](http://www.amazon.com/nRF24L01-Wireless-Transceiver-Arduino-Compatible/dp/B00E594ZX0/ref=pd_sim_indust_5?ie=UTF8&refRID=0R0NHSPAHRSCNGFA1PDN)
- 1x [Moisture Sensor](http://www.amazon.com/Arduino-compatible-Sensitivity-Moisture-Sensor/dp/B00AFCNR3U)
- 1x Plant Jones

Arduino
----
The moisture sensor is attached to the arduino on the 5v pin and analog pin A5. The arduino [measures the moisture](arduino/src/moisture/moisture.ino) level every 30 seconds and sends it to the pi over rf.

Wireless
----
We use this [rf library](https://github.com/edoardoo/RF24) for both the pi and arduino. We based our code off of their examples ([rpi](https://github.com/edoardoo/RF24/blob/master/examples_RPi/gettingstarted.cpp) &  [arduino](https://github.com/edoardoo/RF24/blob/master/examples/GettingStarted/GettingStarted.ino)). Follow their github readme for wiring info.

Note : We found if we tried to have a >= 1 minute delay between arduino transmissions, it would just silently stop transmitting.

Rasberry Pi
----
We use the Rasberry Pi Model B+ running raspbian. The Pi listens for messages from the arduino in [recieve_moisture](pi/src/recieve_moisture.cpp). Tweets are sent through [twitter_functions](src/pi/twitter_functions_server.py). 

The serialized sentiment analysis models take almost 10 minutes to load into memory on the pi which is simply unacceptable in this fast-paced digital plant world we live in. To avoid having to reload these models every time we want to tweet, we have them running as a local socket server. When a tweet needs to be sent, recieve_moisture makes a request to the server with the desired sentiment.

Sentiment Analysis
----
We base our sentiment analyis model on ["Mohammad, Saif M., Svetlana Kiritchenko, and Xiaodan Zhu. "NRC-Canada: Building the state-of-the-art in sentiment analysis of tweets." arXiv preprint arXiv:1308.6242 (2013)."](http://www.umiacs.umd.edu/~saif/WebPages/Abstracts/NRC-SentimentAnalysis.htm). 
    
We use the most discriminative subset of the features from the original paper, word and char ngrams and lexicon dictionaries. We train an SVM model with tuned parameters: rbf kernel, C=100, gamma=.0001. This is all done in [scikit-learn](http://scikit-learn.org/stable/) with a little help from [nltk](http://www.nltk.org/).

The training data was taken from [SemEval 2013 workshop Task 2-B](http://www.cs.york.ac.uk/semeval-2013/task2/index.php?id=data). Our F score on the development set is .65 (the full set of features in the paper gets .69).

The model was trained on a desktop computer, serialized, and sent to the pi to save a long long time. If you do this, make sure your joblib versions match [our models](pi/src/sentiment_analysis/saved_model) were serialized using 0.8.3.

Make Your Own Plant Jones
----
- buy parts -> wire things up.
- load [moisture reader and libraries](arduino/src/) onto arduino.
- on pi
```bash
# install dependencies
sudo apt-get install python-numpy python-scipy python-sklearn

# checkout code
cd to/plant/jones/root
git clone git@github.com:patverga/plant_jones.git
cd plant_jones/pi/src

# set up your twitter secret keys in the form
## apiKey,qwebranapikeyglkj
## apiSecret,labranapisecretio
## accessToken,alrbranaccessogh
## accessTokenSecret,arbranaccessecretgihe
vim .secret_keys

# start server
python twitter_functions_server.py

# once that loads, start recieving moisture from arduino
make && ./recieve_moisture
