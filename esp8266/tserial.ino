#include <microDS18B20.h>

// Define some constants
const int NUM_SENSORS = 5;
const int DPIN_ONEWIRE_BUS = 2;

// And some related to timing
const unsigned long LOOP_TIME = 1000;
const unsigned int REQUEST_OFFSET_TIME = 25;

// Define the addresses of the sensors
const uint8_t SENSOR_ADDRS[NUM_SENSORS][8] PROGMEM = {
  {0x28, 0x4C, 0xD9, 0x43, 0xD4, 0xE1, 0x3C, 0xF8},
  {0x28, 0x1F, 0x5B, 0x43, 0xD4, 0xE1, 0x3C, 0xC7},
  {0x28, 0xD8, 0xB3, 0x43, 0xD4, 0xE1, 0x3C, 0x39},
  {0x28, 0xCE, 0x4F, 0x43, 0xD4, 0xE1, 0x3C, 0x57},
  {0x28, 0x53, 0xF0, 0x43, 0xD4, 0xE1, 0x3C, 0x8C}
};

// Define an object to refer to the sensors
MicroDS18B20<DPIN_ONEWIRE_BUS, DS_ADDR_MODE, NUM_SENSORS, DS_PROGMEM> sensors;

// Define the output format, with spaces for the values
// marked using the @ symbol
const char* const OUTPUT_FMT PROGMEM = "{'a':@,'b':@,'c':@,'d':@,'e':@}";

// Define the time the main loop last ran
unsigned long lastLoopTime = 0;

void setup() {
  // Start serial communication
  Serial.begin(115200);
  delay(500);
  Serial.println("# Started.");
  // Initialize the sensors object with the addresses
  // in program memory
  sensors.setAddress((uint8_t*)SENSOR_ADDRS);
  // Setup each of the sensors
  sensors.setResolutionAll(12);
  // Request the temperature
  sensors.requestTempAll();
}

void loop() {
  // Only run the rest of the function if it's been long enough
  unsigned long currentTime = millis();
  if (((currentTime - lastLoopTime) <= LOOP_TIME)) {
    unsigned int timeBeforeNext = (unsigned int)(LOOP_TIME - (currentTime - lastLoopTime));
    // Just delay if there's enough time left
    if (timeBeforeNext > 150) delay(100);
    // Request if it's at the right time beforehand
    if (timeBeforeNext < REQUEST_OFFSET_TIME) sensors.requestTempAll();
    return;
  }
  // Skip the first measurement
  if (lastLoopTime != 0) {
    // Read all of the sensors and report their values
    // We do this by iterating through OUTPUT_FMT
    int sensor_index = 0;
    for (const char* p = OUTPUT_FMT; *p != '\0'; p += sizeof(char)) {
      if (*p == '@') {
        Serial.print(sensors.getTemp(sensor_index++));
      } else {
        Serial.print(*p);
      }
    }
    Serial.println();
  }
  lastLoopTime = millis();
}
