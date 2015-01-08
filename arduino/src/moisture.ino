#include <SPI.h>
#include "nRF24L01.h"
#include "RF24.h"
#include "printf.h"

// Hardware configuration: Set up nRF24L01 radio on SPI bus plus pins 7 & 8 
RF24 radio(7,8);

byte addresses[][6] = {"1Node","2Node"};

const int PIN = 5;
const int MOISTURE_LEVEL = 250;
const int DELAY = 3600000;

void setup() {
  Serial.begin(57600);
  printf_begin();

  // Setup and configure rf radio
  radio.begin();                          // Start up the radio
  radio.setAutoAck(1);                    // Ensure autoACK is enabled
  radio.setRetries(15,15);                // Max delay between retries & number of retries
  radio.openWritingPipe(addresses[0]);
  radio.openReadingPipe(1,addresses[1]);
  radio.printDetails();                   // Dump the configuration of the rf unit for debugging
}

void loop(void){
  int moisture = analogRead(PIN);
  printf("Sending moisture %d... ", moisture);
    
  radio.stopListening();                                    // First, stop listening so we can talk.
    
  unsigned long time = micros();
    
  if (!radio.write( &moisture, sizeof(int) )){  printf("failed.\n\r");  }
        
  radio.startListening();                                    // Now, continue listening
    
  unsigned long started_waiting_at = micros();               // Set up a timeout period, get the current microseconds
  boolean timeout = false;                                   // Set up a variable to indicate if a response was received or not
    
  while ( ! radio.available() ){                             // While nothing is received
    if (micros() - started_waiting_at > 200000 ){            // If waited longer than 200ms, indicate timeout and exit while loop
      timeout = true;
      break;
    }      
  }
        
  if ( timeout ){                                             // Describe the results
        printf("Failed, response timed out.\n\r");
    }else{
        unsigned long got_time;                                 // Grab the response, compare, and send to debugging spew
        radio.read( &got_time, sizeof(unsigned long) );

        printf("Sent %d, Got response %lu, round-trip delay: %lu microseconds\n\r",moisture,got_time,micros()-got_time);
    }

    delay(DELAY);
}

