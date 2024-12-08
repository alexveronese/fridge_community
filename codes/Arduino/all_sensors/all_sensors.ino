#include <SimpleDHT.h>

SimpleDHT11 dht11;       //instantiates the SimpleDHT11 Object class to variable dht11
const int buttonPin = 2;   //0 = fridge closed; 1 = fridge open
const int pinDHT11int = 5;
const int pinDHT11ext = 6;

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

unsigned long timestamp;

const byte arduinoID = 0x01;      // unique ID Arduino: change this for each device

void setup() {
  Serial.begin(9600);
  timestamp = millis();
  pinMode(buttonPin, INPUT);
}

void loop() {
  if(millis() - timestamp > 5000){      //delay
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

    
    Serial.write(0xFF);              //255: init char
    Serial.write(arduinoID);         //ID Arduino 
    Serial.write(buttonState);
    Serial.write(conv_temperatureIn);
    Serial.write(conv_humidityIn);
    Serial.write(conv_temperatureOut);
    //Serial.write(conv_humidityOut);
    Serial.write(potentiometerValue);
    Serial.write(0xFE);               //254: end char
  
    timestamp = millis();
  }
}
