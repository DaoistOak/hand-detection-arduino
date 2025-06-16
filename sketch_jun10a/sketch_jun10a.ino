void setup() {
  Serial.begin(9600);
  
  for(int pin = 9; pin <= 13; pin++) {
    pinMode(pin, OUTPUT);
    digitalWrite(pin, LOW);
  }
}

void loop() {
  
  if (Serial.available() > 0) {
    char cmd = Serial.read();
    
    if (cmd == 'L') {
      while(Serial.available() > 0) {
        Serial.read();
      }
      
      unsigned long startTime = millis();
      while (Serial.available() < 5 && (millis() - startTime < 1000)) {
        delay(1);
      }
      
      if (Serial.available() >= 5) {
        int previousCount = 0;
        int currentCount = 0;
        
        for(int pin = 9; pin <= 13; pin++) {
          if (digitalRead(pin) == HIGH) {
            previousCount++;
          }
        }
        
        for(int pin = 9; pin <= 13; pin++) {
          int state = Serial.read();
          if (state == 0 || state == 1) {
            digitalWrite(pin, state);
            if (state == HIGH) {
              currentCount++;
            }
          }
        }
        
      }
    }
  }
}
