// Arduino 101 - BLE LED Toggle
// Uses CurieBLE to expose a writable characteristic that controls the LED.

#include <CurieBLE.h>

const int LED_PIN = 13;

// Custom service and characteristic UUIDs.
// Keep these in sync with the Python client.
BLEService ledService("19B10000-E8F2-537E-4F6C-D104768A1214");
BLEByteCharacteristic ledChar("19B10001-E8F2-537E-4F6C-D104768A1214", BLERead | BLEWrite);

void setup() {
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);

  Serial.begin(9600);
  while (!Serial) {
    ;
  }

  BLE.begin();
  BLE.setLocalName("Arduino101-LED");
  BLE.setDeviceName("Arduino101-LED");
  BLE.setAdvertisedService(ledService);

  ledService.addCharacteristic(ledChar);
  BLE.addService(ledService);

  ledChar.writeValue((byte)0);

  BLE.advertise();
}

void loop() {
  BLEDevice central = BLE.central();

  if (central) {
    while (central.connected()) {
      if (ledChar.written()) {
        byte value = ledChar.value();
        digitalWrite(LED_PIN, value ? HIGH : LOW);

        switch (value) {
          case 'w':
            Serial.println("forward");
            break;
          case 's':
            Serial.println("backward");
            break;
          case 'a':
            Serial.println("left");
            break;
          case 'd':
            Serial.println("right");
            break;
          default:
            break;
        }
      }
    }
  }
}
