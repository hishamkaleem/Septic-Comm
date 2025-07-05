#include <AM2320.h>
#include <Wire.h>
#include <Notecard.h>

#define prodID "com.gmail.hishamkaleem27:werlsensordata" //Project ID (REPLACE WITH OWN)

Notecard mycard; //Notecard decleration
AM2320 temp;

float tank_depth = 150;  //Tank depth in cm
float sample_increment = 30; //Sample increment
const int num_sensors = 2; //# of sensors

struct Sensor { //Sensor struct
  const char* name;
  int pin;
};

Sensor sensors[num_sensors] = {{"Potentiometer", 39},{"Temperature", 0}}; //Global sensor array

double getDataUsage(){
  J* req = NoteNewRequest("card.usage.get");
  int sent, received;
  if (req != NULL) {
    JAddStringToObject(req, "mode", "total");
    J* rsp = mycard.requestAndResponse(req);
    if (rsp != NULL) {
      sent = JGetInt(rsp, "bytes_sent");
      received = JGetInt(rsp, "bytes_received");
    }
  }
  double dataUsage = (double)(sent + received)/1000000.0;
  return dataUsage;
}

void formatSend(float depth, float* dataArr) {
  J* req = mycard.newRequest("note.add"); 
  if (req != NULL) {
    JAddStringToObject(req, "file", "tankdata.qo");

    J* body = JCreateObject(); 
    JAddNumberToObject(body, "Tank Depth", depth);

    for (int i = 0; i < num_sensors; i++) {
      JAddNumberToObject(body, sensors[i].name, dataArr[i]);
    }

    double dataUsage = getDataUsage();
    JAddNumberToObject(body, "Total Data Usage (MB): ", dataUsage);

    JAddItemToObject(req, "body", body);
    mycard.sendRequest(req);
  }
  J* syncReq = NoteNewRequest("hub.sync");
  JAddBoolToObject(syncReq, "allow", true);
  mycard.sendRequest(syncReq);

}

void tankSample(float depth) { //Sample tank with all sensors
  float dataArr[num_sensors] = {};
  dataArr[0] = analogRead(39);
  if (temp.measure()){
    dataArr[1] = temp.getTemperature();
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
    JAddStringToObject(setReq, "mode", "continuous"); //Min mode set
    mycard.sendRequest(setReq);
  }

  temp.begin();
} 

void loop() {
  bool connected = false;
  bool timeSet = false;

  for (int i = 0; i < 10 && !connected; i++) {
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

  if (connected) {
    for (int i = 0; i < 10 && !timeSet; i++) {
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

  if (connected && timeSet) {
    tankSample(30);
  } else {
    Serial.println("Sampling skipped: connection or time not ready.");
  }
  delay(10000);  // Wait before trying again
}
