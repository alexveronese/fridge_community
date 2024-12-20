#include <SimpleDHT.h>

SimpleDHT11 dht11;       //instantiates the SimpleDHT11 Object class to variable dht11
const int buttonPin = 2;   //0 = fridge closed; 1 = fridge open
const int pinDHT11int = 5;
const int pinDHT11ext = 6;
const int BUZZER_PIN = 3;
const int MAX_TEMP = 7;


int buttonState = 0;              // open/close
float temperatureIn = 0.0;        // internal temperature and humidity
float humidityIn = 0.0;
int conv_temperatureIn = 0;       // values casted to int
int conv_humidityIn = 0;
float temperatureOut = 0.0;       // external temperature and humidity
float humidityOut = 0.0;
int conv_temperatureOut = 0;      // values casted to int
int conv_humidityOut = 0;
int potentiometerValue = 0;       // power consumption
byte temp_alarm = 0;

unsigned long timestamp;
unsigned long openFridgeTime;

const byte arduinoID = 0x01;      // unique ID Arduino: change this for each device

void setup() {
  Serial.begin(9600);
  timestamp = millis();
  openFridgeTime = millis();
  pinMode(buttonPin, INPUT);
  pinMode(BUZZER_PIN, OUTPUT);
}

void loop() {
    //read the button value
    buttonState = digitalRead(buttonPin);

    //read the potentiometer value
    potentiometerValue = analogRead(A0);
    potentiometerValue = map(potentiometerValue, 0, 1023, 0, 253);

    //read internal temperature and humidity values
    byte dataInt[40] = {0};
    if (dht11.read2(pinDHT11int, &temperatureIn, &humidityIn, dataInt)) {
      Serial.println("Read DHT11 failed");
      return;
    }

    //read external temperature and humidity values
    byte dataExt[40] = {0};
    if (dht11.read2(pinDHT11ext, &temperatureOut, &humidityOut, dataExt)) {
      Serial.print("Read DHT11 failed");
      return;
    }
    // check data
    if(temperatureIn > MAX_TEMP){
        temp_alarm = 1;
    }

    if(buttonState == 0){
        openFridgeTime = millis();
    } else if(millis() - openFridgeTime > 15000){
        // until closed
        while(digitalRead(buttonPin)){
            digitalWrite(BUZZER_PIN, HIGH);
        }
        digitalWrite(BUZZER_PIN,LOW);
        openFridgeTime = millis();
    }
    //se passa abbastanza tempo invio i dati
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
    conv_humidityOut = (int)(round(humidityOut));

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
    //Serial.write(conv_humidityOut);
    Serial.write(potentiometerValue);
    Serial.write(temp_alarm);
    Serial.write(0xFE);               //254: end char
  
    timestamp = millis();
  }
}
