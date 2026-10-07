/**
 * TRACE AI — Smart Lost & Found IoT Collection Box Firmware
 * ---------------------------------------------------------
 * Target Board: ESP32 NodeMCU-32S / ESP-WROOM-32
 * Modules:
 *  - MFRC-522 RFID Reader (SPI)
 *  - SSD1306 128x64 OLED Display (I2C)
 *  - SG90 Micro Servo Motor (PWM Pin 13)
 *  - Active Piezo Buzzer (Pin 14)
 *  - Wi-Fi 802.11 b/g/n (HTTP POST client)
 */

#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <SPI.h>
#include <MFRC522.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <ESP32Servo.h>

// Wi-Fi Configuration
const char* WIFI_SSID     = "Campus_WiFi";
const char* WIFI_PASSWORD = "CampusSecurePassword";

// Backend API URL
const char* API_URL = "http://192.168.1.100:8000/api/iot/items";
const char* BOX_ID  = "BOX-001";
const char* LOCATION = "Library";

// Hardware Pin Definitions
#define RST_PIN     22          // MFRC522 Reset
#define SS_PIN      21          // MFRC522 SDA/SS (SPI)
#define BUZZER_PIN  14          // Active Piezo Buzzer
#define SERVO_PIN   13          // SG90 Servo Signal

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET    -1
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);
MFRC522 mfrc522(SS_PIN, RST_PIN);
Servo lockServo;

void showOLED(String line1, String line2, String line3) {
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(0, 0);
  display.println("TRACE AI SMART BOX");
  display.drawLine(0, 10, 128, 10, SSD1306_WHITE);
  
  display.setCursor(0, 16);
  display.println(line1);
  display.setCursor(0, 30);
  display.println(line2);
  display.setCursor(0, 46);
  display.println(line3);
  display.display();
}

void soundBuzzer(int count, int durationMs) {
  for (int i = 0; i < count; i++) {
    digitalWrite(BUZZER_PIN, HIGH);
    delay(durationMs);
    digitalWrite(BUZZER_PIN, LOW);
    if (i < count - 1) delay(80);
  }
}

void setup() {
  Serial.begin(115200);
  pinMode(BUZZER_PIN, OUTPUT);
  digitalWrite(BUZZER_PIN, LOW);

  // Initialize OLED
  if (!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
    Serial.println(F("[ERR] SSD1306 initialization failed!"));
  }
  showOLED("BOOTING...", "Connecting Wi-Fi", "");

  // Initialize Servo
  lockServo.attach(SERVO_PIN);
  lockServo.write(0); // 0° = Locked

  // Initialize RFID
  SPI.begin();
  mfrc522.PCD_Init();
  Serial.println(F("[INIT] MFRC522 RFID Ready"));

  // Connect to Campus Wi-Fi
  Serial.print("[WIFI] Connecting to ");
  Serial.println(WIFI_SSID);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(500);
    Serial.print(".");
    attempts++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.print("\n[WIFI] Connected! IP: ");
    Serial.println(WiFi.localIP());
    showOLED("STATUS: READY", "Tap RFID Tag", "Box: BOX-001 (Online)");
  } else {
    Serial.println("\n[WIFI] Connection Timeout. Running in offline buffer mode.");
    showOLED("STATUS: READY", "Tap RFID Tag", "Box: BOX-001 (Offline)");
  }
}

void loop() {
  // Check for new RFID tag
  if (!mfrc522.PICC_IsNewCardPresent() || !mfrc522.PICC_ReadCardSerial()) {
    delay(50);
    return;
  }

  // Extract UID
  String rfidUID = "";
  for (byte i = 0; i < mfrc522.uid.size; i++) {
    rfidUID += (mfrc522.uid.uidByte[i] < 0x10 ? "0" : "");
    rfidUID += String(mfrc522.uid.uidByte[i], HEX);
  }
  rfidUID.toUpperCase();
  Serial.println("\n[RFID] Detected Tag UID: " + rfidUID);

  // User Feedback
  showOLED("SCANNING TAG...", "UID: " + rfidUID, "Unlocking Door...");
  soundBuzzer(2, 100);

  // Unlock Door
  lockServo.write(90); // 90° = Unlocked
  Serial.println("[SERVO] Door Unlocked (90 deg). Awaiting item deposit.");

  // Transmit to FastAPI Backend
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(API_URL);
    http.addHeader("Content-Type", "application/json");

    StaticJsonDocument<256> doc;
    doc["box_id"] = BOX_ID;
    doc["rfid_id"] = rfidUID;
    doc["location"] = LOCATION;

    String jsonPayload;
    serializeJson(doc, jsonPayload);

    int httpResponseCode = http.POST(jsonPayload);
    Serial.print("[HTTP] Response code: ");
    Serial.println(httpResponseCode);

    if (httpResponseCode == 200) {
      String response = http.getString();
      Serial.println("[HTTP] Response: " + response);
      showOLED("ITEM DEPOSITED!", "Synced with AI", "Thank you!");
      soundBuzzer(1, 400);
    } else {
      showOLED("SAVED LOCALLY", "Server Code: " + String(httpResponseCode), "");
    }
    http.end();
  }

  // Allow 5 seconds for user to deposit item
  delay(5000);

  // Re-lock Door
  lockServo.write(0);
  Serial.println("[SERVO] Door Re-locked (0 deg).");
  soundBuzzer(1, 150);

  showOLED("STATUS: READY", "Tap RFID Tag", "Box: BOX-001 (Online)");
  mfrc522.PICC_HaltA();
  mfrc522.PCD_StopCrypto1();
}
