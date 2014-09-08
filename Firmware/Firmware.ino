// Includes
#include <Servo.h>

byte state = 0;                          // The current state. States are: 0 - waiting for start, 1-3 - waiting for yaw, 4-6 - waiting for pitch
unsigned long lastCommandTime;           // A variable to hold the last time a command was received over the serial line. Used to detect if a "timeout" has occured

String yawValue = "";                    // Two strings to hold the desired incoming (over serial) yaw and pitch values
String pitchValue = "";

Servo SRV_YAW;                          // Two servo objects. We need one for each controlled servo
Servo SRV_PITCH;

void setup() {
  Serial.begin(9600);			// opens serial port, sets data rate to 9600 bps
  
  SRV_YAW.attach(9);			// Attaches the yaw servo to pin 9
  SRV_PITCH.attach(8);			// Attaches the pitch servo to pin 10
  
  SRV_YAW.write(90);                    // Centers the yaw servo
  SRV_PITCH.write(90);                  // Centers the pitch servo
  
  Serial.println("#System Start");      // Output a comment (#) letting the user/program know the program has started
  Serial.println("$Version:1.0");       // Output a variable ($) letting the user/program know the firmware version number
}

void loop() {
  // Check for the timeout condition. If a timout has occured reset the state and let the user/program know of the event (!)
  if(millis() > lastCommandTime + 1000)
  {
    state = 0;
    Serial.println("!Timeout");
    lastCommandTime = millis();
  }
  
  // Processing incoming serial commands while we still have incoming bytes to process
  while (Serial.available() > 0) {
    lastCommandTime = millis();          // Reset the timeout clock
    int inChar = Serial.read();          // Pop a byte off of the incoming serial queue
    Serial.print("$State:");             // Debug the current state. Send it as a variable ($)
    Serial.println(state,DEC);
    if((state == 0) && (inChar == '>'))  // State the state machine. Looking for the first character ">"
    {
      state++;
    }
    else if((state > 0) && (state < 4))  // The next section of the state machine. Looking for yawValues. Builds up the yawValue string with incoming characters for later processing
    {
      yawValue += (char)inChar; 
      state++;
    }
    else if((state > 3) && (state <= 6))
    {
      pitchValue += (char)inChar; 
      state++;
    }
    else if (state > 6)                  // The end of the state machine. Outputs the yaw and pitch values and sends them to the servos
    {
      state = 0;  
      SRV_YAW.write(yawValue.toInt());                    // Send the desired yaw value to the yaw servo
      SRV_PITCH.write(pitchValue.toInt();                  // Send the desired pitch value to the pitch servo
      Serial.print("$YawValue:");
      Serial.println(yawValue.toInt());
      Serial.print("$PitchValue:");
      Serial.println(pitchValue.toInt());
      Serial.println("$Wrench");
      yawValue = "";
      pitchValue = "";
      Serial.println("!ACK");
    }
    else
    {
      state = 0;
      Serial.println("#Invalid Command Sequence");
      Serial.println("!NAK");
    }
  }
}


















