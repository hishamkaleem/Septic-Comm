#include <Wire.h>
#include <Notecard.h>

#define prodID "com.gmail.hishamkaleem27:werlsensordata" //Project ID (REPLACE WITH OWN)

Notecard mycard; //Notecard decleration

const float tank_depth = 150;  //Tank depth in cm
const float sample_increment = 30; //Sample increment
const int num_sensors = 6; //# of sensors

struct Sensor { //Sensor struct
  const char* name;
  int pin;
};

Sensor sensors[num_sensors] = {}; //Global sensor array

void formatSend(float depth, float* dataArr) { //Format data and sync to notehub
  J* req = mycard.newRequest("note.add");
  if (req != NULL) {
    JAddStringToObject(req, "file", "tankdata.qo"); //Queue data
    JAddBoolToObject(req, "sync", true); // Sync forcefully (min mode)
    JAddNumberToObject(req, "Tank Depth", depth);
    
    J* timeReq = mycard.newRequest("time.get"); // Timestamp object
    J* timeRsp = mycard.sendRequest(timeReq);
    if (timeRsp) {
      const char* timeStr = JGetString(timeRsp, "time");
      if (timeStr) {
        JAddStringToObject(req, "Logged Time", timeStr);
      }
      JDelete(timeRsp);
    }
    J* body = JCreateObject();
    for (int i = 0; i < num_sensors; i++) {
      JAddNumberToObject(body, sensors[i].name, dataArr[i]);
    }
    JAddItemToObject(req, "body", body);
    mycard.sendRequest(req);
  }
}

void tankSample(float depth) { //Sample tank with all sensors
  float dataArr[num_sensors] = {};
  for (int i = 0; i < num_sensors; i++) {
    dataArr[i] = analogRead(sensors[i].pin);
  }
  formatSend(depth, dataArr);
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
    JAddStringToObject(setReq, "mode", "minimum"); //Min mode set
    mycard.sendRequest(setReq);
  }

  J* timeReq = mycard.newRequest("time.set"); //Sync real time for timestamping
  if (timeReq){
    JAddStringToObject(req, "mode", "auto");
    mycard.sendRequest(req);
  }
}

void loop() {
  float depth = 0;
  while (depth < tank_depth){ //Reverse if depth value increases
    depth = analogRead( ); //Read servo depth
    if (depth % sample_increment == 0){
      tankSample(depth);
    }
  }  
  delay( ); //Wait for 24 hrs
}
