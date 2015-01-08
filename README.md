# plant_jones

![This is me](https://pbs.twimg.com/profile_images/553022075774840832/MPafmt1D.jpeg)

Plant Jones is a semi-intelligent, non-autonomous plant. He is capable of measuring, analyzing, and alerting others to his own moisture needs. 

Plant Jones also possesses [not quite developed social skills](https://twitter.com/plant_jones). He is able to parse tweets from human users and determine their sentiment at a rate statistically significantly above random chance. He uses these analyzed tweets to transmit information about his thirst levels in the hopes of garnering pity and water. 

Parts
----
- 1x Arduino Uno
- 1x Rasberry Pi Model B+
- 2x [nRf24L01+ Tranciever](http://www.amazon.com/nRF24L01-Wireless-Transceiver-Arduino-Compatible/dp/B00E594ZX0/ref=pd_sim_indust_5?ie=UTF8&refRID=0R0NHSPAHRSCNGFA1PDN)
- 1x [Moisture Sensor](http://www.amazon.com/Arduino-compatible-Sensitivity-Moisture-Sensor/dp/B00AFCNR3U)
- 1x Plant Jones

Arduino
----
The moisture sensor is attached to the arduino on the 5v pin and an analog pin (we use A5).

Wireless
----
We use this [rf library](https://github.com/edoardoo/RF24) for both the pi and arduino. We based our code off of their examples ([rpi](https://github.com/edoardoo/RF24/blob/master/examples_RPi/gettingstarted.cpp) &  [arduino](https://github.com/edoardoo/RF24/blob/master/examples/GettingStarted/GettingStarted.ino)). Follow their github readme for wiring info.

Rasberry Pi
----
We use the Rasberry Pi Model B+ running raspbian. The pi recieves the moisture reading from the arduino every hour. If the moisture level is too low, Plant Jones scours twitter for negative tweets about water to display his sadness in a way relevant to his needs. If the moisture levels gain a sudden spike, Plant Jones tweets a positive tweet about water signaling how happy he is.

Sentiment Analysis
----
The model is an SVM from scikit-learn. We use this [Twitter Sentiment Analysis dataset](http://thinknook.com/wp-content/uploads/2012/09/Sentiment-Analysis-Dataset.zip). We used a simple bag of words model because we didn't try very hard. We used only a subset of the data for training (10k is quick, 100k is fine). Be sure to randomly shuffle the dataset as it is in alphabetical order.
