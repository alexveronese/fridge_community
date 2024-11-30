/*
  Button

  Turns on and off a light emitting diode(LED) connected to digital pin 13,
  when pressing a pushbutton attached to pin 2.

  The circuit:
  - pushbutton attached to pin 2 from +5V
  - 10K resistor attached to pin 2 from ground
*/

// constants won't change. They're used here to set pin numbers:
const int buttonPin = 2;  // the number of the pushbutton pin

//0 = FRIGO CHIUSO
//1 = FRIGO APERTO

// variables will change:
int buttonState = 0;  // variable for reading the pushbutton status

unsigned long timestamp;

void setup() {
  Serial.begin(9600);
  timestamp = millis();
  // initialize the pushbutton pin as an input:
  pinMode(buttonPin, INPUT);
}

void loop() {
  if(millis() - timestamp > 2000){
    // read the state of the pushbutton value:
    buttonState = digitalRead(buttonPin);

    Serial.write(0xFF);
    Serial.write(buttonState);
    Serial.write(0xFE);

    Serial.println(buttonState);

    timestamp = millis();
  }
}
