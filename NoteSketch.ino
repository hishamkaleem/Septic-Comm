#include <AM2320.h>
#include <Wire.h>
#include <Notecard.h>

#define prodID "com.gmail.hishamkaleem27:werlsensordata" //Project ID (REPLACE WITH OWN)

Notecard mycard; //Notecard decleration
AM2320 temp;

const int num_sensors = 6; //# of sensors

struct Sensor { //Sensor struct
  const char* name;
  int pin;
};

Sensor sensors[num_sensors] = {{"Turbidity", 2}, {"Potentiometer", 3}, {"Light", 4}, {"Infrared", 5}, {"Magnetic", 6}, {"Temperature", 0}}; //DEFINE SENSOR NAMES PROPERLY FOR PROPER PLOTTING

void formatSend(float depth, float* dataArr) {
  J* req = mycard.newRequest("note.add"); 
  if (req != NULL) {
    JAddStringToObject(req, "file", "tankdata.qo"); //Create a new file

    // Add all data to the request body
    J* body = JCreateObject(); 
    JAddNumberToObject(body, "Tank Depth", depth);

    for (int i = 0; i < num_sensors; i++) {
      JAddNumberToObject(body, sensors[i].name, dataArr[i]);
    }

    JAddItemToObject(req, "body", body);
    mycard.sendRequest(req);
  }

  // Send a sync request to Notehub to ensure data is sent immediately
  J* syncReq = NoteNewRequest("hub.sync");
  JAddBoolToObject(syncReq, "allow", true);
  mycard.sendRequest(syncReq);
}

 //Sample tank with all sensors
void tankSample(float depth) {
  float dataArr[num_sensors] = {};
  for (int i = 0; i < num_sensors-1; i++){
    dataArr[i] = analogRead(sensors[i].pin);
  }
  if (temp.measure()){ //Test for temperature sensor (remove if not using)
     dataArr[5] = temp.getTemperature();
  }
  formatSend(depth,dataArr);
}

void setup() {
  Serial.begin(115200); //Serial debugging
  while (!Serial);

  Wire.begin(); //Setup i2c
  mycard.begin(); //Setup notecard
  mycard.setDebugOutputStream(Serial);

  J* setReq = mycard.newRequest("hub.set");
  if (setReq) {
    JAddStringToObject(setReq, "product", prodID); //Project set
    JAddStringToObject(setReq, "mode", "continuous"); //Mode set
    mycard.sendRequest(setReq);
  }
  temp.begin();
} 

void loop() {
  bool connected = false;
  bool timeSet = false;

  // Wait for Notehub connection to be set
  while (!connected) {
    J* statusReq = NoteNewRequest("card.status");
    J* statusRsp = mycard.requestAndResponse(statusReq);
    if (statusRsp != NULL) {
      connected = JGetBool(statusRsp, "connected");
      JDelete(statusRsp);
      if (!connected) {
        Serial.println("Waiting for Notehub connection...");
        delay(5000);
      }
    }
  }

  // Wait for time to be set
  if (connected) {
    while(!timeSet) {
      J* timeReq = NoteNewRequest("card.time");
      J* timeRsp = mycard.requestAndResponse(timeReq);
      if (timeRsp != NULL) {
        timeSet = true;
      } 
      else {
        Serial.println("Waiting for time to be set...");
      }
      JDelete(timeRsp);
      if (!timeSet) delay(5000);
    }
  }

  // If connected and time is set, start sampling
  int x = 30;
  int dat = 0;
  while (connected && timeSet){
    tankSample(x);
    dat++;
    Serial.println(dat);
    x += 30;
    if (x > 150){
      x = 30;
    }
    delay(15000); //Change delay to desired sampling rate
  }
}



// DATA USAGE FOR 100 CONSECUTIVE REQUESTS (6 sensors, 15 sec delay):
//**********************************************************************************
//CURRENT DATA USAGE: 1.66 MB

//END DATA USAGE: 1.76 MB

//APPROXIMATE DATA USAGE PER REQUEST: (1.76 MB - 1.66 MB)/100  = 1.00 KB
//**********************************************************************************


// DATA USAGE FOR 50 SEPERATED REQUESTS (6 sensors, 15 sec delay, 5 depths, 10 samples):
//***********************************************************************************
// CURRENT DATA USAGE: 1.76 MB

// END DATA USAGE: 2.08 MB

// APPROXIMATE DATA USAGE PER REQUEST: (2.08 MB - 1.76 MB)/50 = 6.4 KB 
//*********************************************************************************** 