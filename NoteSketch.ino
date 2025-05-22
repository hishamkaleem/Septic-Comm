#include <Wire.h>
#include <Notecard.h>

#define prodID "com.gmail.hishamkaleem27:werlsensordata" //Project ID (REPLACE WITH OWN)

Notecard mycard; //Notecard decleration

float tank_depth = 150;  //Tank depth in cm
float sample_increment = 30; //Sample increment
const int num_sensors = 6; //# of sensors

struct Sensor { //Sensor struct
  char* name;
  int pin;
};

Sensor sensors[num_sensors] = {}; //Global sensor array

void formatSend(float depth, float* dataArr) {
  J* timeReq = NoteNewRequest("card.time");
  J* timeRsp = mycard.requestAndResponse(timeReq); //Timestamp

  J* req = mycard.newRequest("note.add");
  if (req != NULL) {
    JAddStringToObject(req, "file", "tankdata.qo");
    JAddBoolToObject(req, "sync", true);

    J* body = JCreateObject();
    JAddNumberToObject(body, "Tank Depth", depth);
    for (int i = 0; i < num_sensors; i++) {
      JAddNumberToObject(body, sensors[i].name, dataArr[i]);
    }
    JAddItemToObject(req, "body", body);
    mycard.sendRequest(req);
  }
}

void tankSample(float depth) { //Sample with all sensors
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
    JAddStringToObject(setReq, "mode", "continuous"); //Cont mode set
    mycard.sendRequest(setReq);
  }
}
void loop() {
  bool connected = false;

  for (int i = 0; i < 10 && !connected; i++) { //Wait for hub connection
    J* statusReq = NoteNewRequest("card.status");
    J* statusRsp = mycard.requestAndResponse(statusReq);
    if (statusRsp != NULL) {
      connected = JGetBool(statusRsp, "connected");
      JDelete(statusRsp);
    }
    if (!connected) {
      Serial.println("Waiting for Notehub connection...");
      delay(5000);  // Wait 5 secs before retry
    }
  }

  if (connected) {
    float depth = 0;
    while (depth < (tank_depth - 20)){ //Reverse if depth value increases + adjustment factor
      depth = analogRead( ); //Read servo depth
      if (int(depth) % int(sample_increment) == 0){
        tankSample(depth);
      }
    }  
  }
  delay( ); //Wait for 24 hrs
}
