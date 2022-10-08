#include <ArduinoMqttClient.h>
#include <DHT.h>
#include <DHT_U.h>
#include <WiFiNINA.h>
#include "secrets.h"
#include "defines.h"

#define waterLevelPin A1
#define waterLevelPowerPin 0

#define DHTPIN 5
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

//RelayModule
const int tentLightPin = 1;
const int waterPumpPin = 2;

// 30 seconds without delay
const long interval = 30000;
unsigned long previousMillis = 0;

// Work in progress
bool lightStatus = false;
bool pumpStatus = false;
bool lowWaterStatus;
int waterLevelValue;
int currentWaterLevel;

// Will
String willPayload = "Stormie RIP";
bool willRetain = false;
int MQTTQos = 0;
bool retained = false;
bool dup = false;

// wifi & mqtt
WiFiClient wifiClient;
MqttClient mqttClient(wifiClient);

// mqtt BROKER
const char broker[] = "10.0.0.133";
int port = 1883;
const char willTopic[] = "stormie/will";
const char TemperatureTopic[] = "acontrolledstorm/temperature";
const char HumidityTopic[] = "acontrolledstorm/humidity";
const char WaterLevelTopic[] = "acontrolledstorm/waterlevel";

// Stormie Commands.     INCOMPLETE*************
const char cmdLightsOn[] = "CMDMKR101";
const char cmdLghtsOff[] = "CMDMKR100";
const char cmdPumpOn[] = "CMDMKR201";
const char cmdPumpOff[] = "CMDMKR200";


// setup
void setup() {
  Serial.begin(115200);
  delay(2000);

  dht.begin();
  Serial.println("DHT Active");

  pinMode(tentLightPin, OUTPUT);
  digitalWrite(tentLightPin, HIGH);
  lightStatus = 1;
  Serial.println("Tent Lights HIGH;");

  pinMode(waterPumpPin, OUTPUT);
  digitalWrite(waterPumpPin, LOW);
  pumpStatus = 0;
  Serial.println("Water Pump LOW");

  pinMode(waterLevelPowerPin, OUTPUT);
  digitalWrite(waterLevelPowerPin, LOW);
  Serial.println("waterlevel Power Pin LOW");

  Serial.println("Starting WiFi...");

  while (WiFi.begin(ssid, password) != WL_CONNECTED) {
    Serial.print(".");
    delay(1000);
  }
  Serial.println("Connected to WiFi");
  Serial.println();

  mqttClient.setId("STORMIE");
  mqttClient.setUsernamePassword(mqttUser, mqttPasswd);
  // mqttClient.setCleanSession(false);    // default=true

  mqttClient.beginWill(willTopic, willPayload.length(), willRetain, MQTTQos);
  mqttClient.print(willPayload);
  mqttClient.endWill();

  Serial.print("Attempting to connect to the MQTT broker: ");
  Serial.println(broker);

  if (!mqttClient.connect(broker, port)) {
    Serial.print("MQTT connection failed! Error code = ");
    Serial.println(mqttClient.connectError());
    while (1)
      ;
  }

  Serial.println("Connected to the MQTT Broker!");
  // mqttClient.onMessage(onMqttMessage);
  mqttClient.subscribe(TemperatureTopic, MQTTQos);
  mqttClient.subscribe(HumidityTopic, MQTTQos);
  mqttClient.subscribe(WaterLevelTopic, MQTTQos);
  Serial.println("Subbed to Temperature, Humidity, WaterLevel");
  Serial.println();
}

void loop() {
  mqttClient.poll();
  unsigned long currentMillis = millis();
  if (currentMillis - previousMillis >= interval) {
    previousMillis = currentMillis;
    checkDHT();
    checkWaterLevel();
    Serial.println();
  }
}

void checkDHT() {
  float dhttemperature = dht.readTemperature();
  int dhthumidity = dht.readHumidity();

  Serial.print("Temperature: ");
  Serial.println(dhttemperature);
  Serial.print("Humidity: ");
  Serial.println(dhthumidity);

  mqttClient.beginMessage(TemperatureTopic);
  mqttClient.print(dhttemperature);
  mqttClient.endMessage();

  mqttClient.beginMessage(HumidityTopic);
  mqttClient.print(dhthumidity);
  mqttClient.endMessage();
}

void checkWaterLevel() {
  digitalWrite(waterLevelPowerPin, HIGH);
  delay(100);
  currentWaterLevel = analogRead(waterLevelPin);
  Serial.print("Current Water Level: ");
  Serial.println(currentWaterLevel);

  mqttClient.beginMessage(WaterLevelTopic);
  mqttClient.print(currentWaterLevel);
  mqttClient.endMessage();
  digitalWrite(waterLevelPowerPin, LOW);

  if (currentWaterLevel <= 200) {
    lowWaterStatus = true;
  } else {
    lowWaterStatus = false;
  }
}

void PumpOn() {
  if (lowWaterStatus == false && lightStatus == true) {
    digitalWrite(waterPumpPin, HIGH);
    pumpStatus = true;
    Serial.println("Pump On!");
  } else {
    Serial.println("Else..Pump not on...hopefully...");
    LowWaterAlert();
    PumpOff();
  }
}

void PumpOff() {
  digitalWrite(waterPumpPin, LOW);
  pumpStatus = 0;
  Serial.println("Pump LOW");
}

void LightsOn() {
  digitalWrite(tentLightPin, HIGH);
  lightStatus = 1;
  Serial.println("Tent Lights HIGH");
}

void LightsOff() {
  digitalWrite(tentLightPin, LOW);
  lightStatus = 0;
  Serial.println("Tent Lights LOW");
}

void LowWaterAlert() {
  Serial.println("LOW WATER PUMP WILL REMAIN OFF!");
}

void resetdevice(){
  Board.resetdevice()
}