#include <cstdlib>
#include <iostream>
#include <sstream>
#include <string>
#include <RF24/RF24.h>
#include <Python.h>

#define MAX_DIGITS 4
#define HISTORY_LEN 5 
#define READ_DELAY 1000 // 1 second
#define TWEET_DELAY 3600000 // 1 hour

using namespace std;

RF24 radio(RPI_BPLUS_GPIO_J8_15,RPI_BPLUS_GPIO_J8_24, BCM2835_SPI_SPEED_8MHZ);

// Radio pipe addresses for the 2 nodes to communicate.
const uint8_t pipes[][6] = {"1Node","2Node"};
const char* pyFileName = "/home/pemma/plant_jones/pi/src/send_tweet_client.py";
const int DRY_THRESHOLD = 500;

void getMoisture(int &buffer);
int avg(int* arr, int len);

int main(int argc, char** argv){

  // Setup and configure rf radio
  radio.begin();
  // optionally, increase the delay between retries & # of retries
  radio.setRetries(15,15);
  //  // Dump the configuration of the rf unit for debugging
  //  radio.printDetails();
  radio.openWritingPipe(pipes[1]);
  radio.openReadingPipe(1,pipes[0]);
  radio.startListening();
  
  FILE* pyFile;
  int moistureHistory [5] = {};
  int currentMoisture;
  int lastSentiment = 1;
  int currentSentiment = 1;
  char ** args = (char**) malloc(sizeof(char*));
  args[0] = (char*) malloc(MAX_DIGITS*sizeof(char));
  int i = 0;
  
  printf("Initializing history array");
  fflush(stdout);
  while (i < HISTORY_LEN){
    if(radio.available())
    {     
        getMoisture(moistureHistory[i]);
        delay(READ_DELAY);
        i++;
    } 
  }
  while(true){
    if(radio.available()){
        // get moisture reading from arduino 
        int historyIndex = i % HISTORY_LEN;       
        getMoisture(moistureHistory[historyIndex]);
        currentMoisture = avg(moistureHistory, HISTORY_LEN);

        // if moisture is too low
        if (lastSentiment && currentMoisture < DRY_THRESHOLD)
            currentSentiment = 0;
        else if(!lastSentiment && currentMoisture > DRY_THRESHOLD){
            currentSentiment = 1;
        }
       
        // we need water or got watered, send tweet
        if (currentSentiment != lastSentiment){
            sprintf(args[0], "%d", currentSentiment);
            Py_Initialize();
            pyFile = fopen( pyFileName,"r");
            Py_SetProgramName(argv[0]);  /* optional but recommended */
            PySys_SetArgv(1, args);
            PyRun_SimpleFile(pyFile, pyFileName);
            Py_Finalize();
            fclose(pyFile);
            delay(TWEET_DELAY);
        }

        printf("Got moisture %d (sentiment=%d)\n", moistureHistory[historyIndex], currentSentiment);	
        lastSentiment = currentSentiment;
        i++;
        delay(READ_DELAY);			        
   }
  } // forever loop

  return 0;
}

int avg(int* arr, int len){
    int sum = 0;
    for(int i = 0; i < len; ++i){
        sum += arr[i];
    }
    return sum/len;
}

void getMoisture(int &buffer){
    while(radio.available()){
        radio.read(&buffer, sizeof(int));
    }
    radio.stopListening();
    radio.write(&buffer, sizeof(int));
    radio.startListening();
}

