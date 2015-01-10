#include <cstdlib>
#include <iostream>
#include <sstream>
#include <string>
#include <RF24/RF24.h>
#include <Python.h>


using namespace std;

RF24 radio(RPI_BPLUS_GPIO_J8_15,RPI_BPLUS_GPIO_J8_24, BCM2835_SPI_SPEED_8MHZ);

// Radio pipe addresses for the 2 nodes to communicate.
const uint8_t pipes[][6] = {"1Node","2Node"};
const char* pyFileName = "pytest.py";
const int DRY_THRESHOLD = 500;
  
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
  
  FILE* pyFile;
  int lastMoisture = 0;
  //char args[1][1024] = {{'0'}};
//  char args[][] = {"0"};
  char ** args = new char *[1];
  args[0] = "0000";
  while (1){
      
    if(radio.available())
    {     
        int sentiment = -1;
        // get moisture reading from arduino
        int moisture;
        while(radio.available()){
            radio.read( &moisture, sizeof(int) );
        }
        radio.stopListening();			
        radio.write( &moisture, sizeof(int) );
        radio.startListening();
        
        // if moisture is too low
        if (moisture < DRY_THRESHOLD)
            sentiment = 0;
       
        // moisture spiked (maybe got wattered)
       // else if (moisture....)
       //     sentiment = 1;

        // we need water or got watered, send tweet
        if (sentiment > -1)
        {
            //itoa(sentiment, args[0], 10)
            sprintf(args[0], "%d", sentiment);
            pyFile = fopen( pyFileName,"r");
            Py_SetProgramName(argv[0]);  /* optional but recommended */
            Py_Initialize();
            PySys_SetArgv(1, args);
            PyRun_SimpleFile(pyFile, pyFileName);
            Py_Finalize();
            fclose(pyFile);
        }

        printf("Got moisture %d...\n", moisture);	
        lastMoisture = moisture;
        delay(1000);			        
   }
  } // forever loop

  return 0;
}

