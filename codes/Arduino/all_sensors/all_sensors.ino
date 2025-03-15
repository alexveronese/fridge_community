#include <SimpleDHT.h>

SimpleDHT11 dht11;              //instantiates the SimpleDHT11 Object class to variable dht11
const int buttonPin = 2;        //0 = fridge closed; 1 = fridge opened
const int pinDHT11int = 5;      //front_view: signal, vcc, gnd
const int pinDHT11ext = 6;
const int BUZZER_PIN = 9;
const int MAX_TEMP = 7;
const int ledPin = 10;


int buttonState = 0;              // open/close
float temperatureIn = 0.0;        // internal temperature and humidity
float humidityIn = 0.0;
float humidityOut = 0.0;
int conv_temperatureIn = 0;       // values casted to int
int conv_humidityIn = 0;
float temperatureOut = 0.0;       // external temperature and humidity
int conv_temperatureOut = 0;      // values casted to int
int conv_humidityOut = 0;
int potentiometerValue = 0;       // power consumption

unsigned long timestamp;
unsigned long timestamp_temp;
unsigned long openFridgeTime;

const byte arduinoID = 0x01;      // unique ID Arduino: change this for each device

void setup() {
  Serial.begin(9600);
  timestamp = millis();
  timestamp_temp = millis();
  openFridgeTime = millis();
  pinMode(buttonPin, INPUT);
  pinMode(BUZZER_PIN, OUTPUT);

}

void loop() {
  //read the button value
  buttonState = digitalRead(buttonPin);
  //Serial.println(buttonState);

  //read the potentiometer value
  potentiometerValue = analogRead(A0);
  potentiometerValue = map(potentiometerValue, 0, 1023, 0, 253);

  //read internal temperature and humidity values
  if(millis() - timestamp_temp > 2000) {
      byte dataInt[40] = {0};
      if (dht11.read2(pinDHT11int, &temperatureIn, &humidityIn, dataInt)) {
        Serial.println("Read internal DHT11 failed\n");
        return;
      } else {
        //Serial.println("OK in");
        Serial.println(temperatureIn);
      }

      //read external temperature and humidity values
      byte dataExt[40] = {0};
      if (dht11.read2(pinDHT11ext, &temperatureOut, &humidityOut, dataExt)) {
        Serial.print("Read external DHT11 failed\n");
        return;
      } else {
        //Serial.println("OK out");
        Serial.println(temperatureOut);
      }

      timestamp_temp = millis();
  }

  if(buttonState == 0){
      openFridgeTime = millis();
  } else if(millis() - openFridgeTime > 10000){
      // until closed
      while(digitalRead(buttonPin)){
          tone(BUZZER_PIN, 500);
          delay(500);
          noTone(BUZZER_PIN);
          delay(500);
          tone(BUZZER_PIN, 100);
      }
      noTone(BUZZER_PIN);
      openFridgeTime = millis();
  }

  if (Serial.available()) {
      int dataAlarm;
      dataAlarm = Serial.read();
      if (dataAlarm == 'A') digitalWrite(ledPin, HIGH);
      if (dataAlarm =='S') digitalWrite(ledPin, LOW);
  }


  if(millis() - timestamp > 5000){      //delay
    //just for debugging
    //Serial.println(temperatureIn);
    //Serial.println(humidityIn);
    //Serial.println(temperatureOut);
    //Serial.println(humidityOut);

    //casting to int
    conv_temperatureIn = (int)(round(temperatureIn));
    conv_humidityIn = (int)(round(humidityIn));
    conv_temperatureOut = (int)(round(temperatureOut));

    //just for debugging
    //Serial.println("converted values:");
    //Serial.println(conv_temperatureIn);
    //Serial.println(conv_humidityIn);
    //Serial.println(temperatureOut); Serial.print("°C, ");
    //Serial.println(humidityOut); Serial.println("%");

    //keep this order, if you change it, check order in bridge_Serial_HTTP
    Serial.write(0xFF);              //255: init char
    Serial.write(arduinoID);         //ID Arduino
    Serial.write(buttonState);
    Serial.write(conv_temperatureIn);
    Serial.write(conv_humidityIn);
    Serial.write(conv_temperatureOut);
    Serial.write(potentiometerValue);
    Serial.write(0xFE);               //254: end char

    timestamp = millis();
  }
}
