#include <cstdlib>
#include <iostream>
#include <sstream>
#include <string>
#include <RF24/RF24.h>

using namespace std;

RF24 radio(RPI_BPLUS_GPIO_J8_15,RPI_BPLUS_GPIO_J8_24, BCM2835_SPI_SPEED_8MHZ);

// Radio pipe addresses for the 2 nodes to communicate.
const uint8_t pipes[][6] = {"1Node","2Node"};

int main(int argc, char** argv){

  // Setup and configure rf radio
  radio.begin();

  // optionally, increase the delay between retries & # of retries
  radio.setRetries(15,15);
  
  // Dump the configuration of the rf unit for debugging
  radio.printDetails();

  radio.openWritingPipe(pipes[1]);
  radio.openReadingPipe(1,pipes[0]);
  radio.startListening();

  while (1){
    if(radio.available()){
      int moisture;

      while(radio.available()){
        radio.read( &moisture, sizeof(int) );
      }
      radio.stopListening();
				
      radio.write( &moisture, sizeof(int) );
      radio.startListening();

      printf("Got moisture %d...\n", moisture);
				
      delay(9000);				
    }
  } // forever loop

  return 0;
}

