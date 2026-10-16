#include <Wire.h>
#include <LiquidCrystal_I2C.h>

#define TRIG 10
#define ECHO 9

// Initialize 16x2 I2C LCD (address 0x27, adjust if needed)
LiquidCrystal_I2C lcd(0x27, 16, 2);

long duration;
int distance;

String notes[] = {"C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"};

void setup() {
  pinMode(TRIG, OUTPUT);
  pinMode(ECHO, INPUT);
  Serial.begin(9600);
  
  // Initialize LCD
  Wire.begin();
  lcd.init();
  lcd.backlight();
  lcd.print("Air Piano Ready!");
  delay(2000);
  lcd.clear();
}

void loop() {
  // Ultrasonic reading
  digitalWrite(TRIG, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG, LOW);

  duration = pulseIn(ECHO, HIGH);
  distance = duration * 0.034 / 2;

  if (distance >= 5 && distance <= 50) {
    int noteIndex = map(distance, 5, 50, 11, 0); // invert
    String noteDisplay = notes[noteIndex];
    
    // Send to serial
    Serial.print("Distance: ");
    Serial.print(distance);
    Serial.print(" cm - Note: ");
    Serial.println(noteDisplay);
    
    // Display on LCD
    lcd.setCursor(0, 0);
    lcd.print("D:");
    lcd.print(distance);
    lcd.print("cm ");
    
    lcd.setCursor(0, 1);
    lcd.print("Note: ");
    lcd.print(noteDisplay);
    lcd.print("   ");  // Clear extra characters
  } else {
    Serial.print("Distance: ");
    Serial.print(distance);
    Serial.println(" cm - Note: none");
    
    // Display on LCD
    lcd.setCursor(0, 0);
    lcd.print("D:");
    lcd.print(distance);
    lcd.print("cm ");
    
    lcd.setCursor(0, 1);
    lcd.print("Note: None      ");
  }

  delay(50);
}
