/* ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** 
 * AI + IoT SMART LOST & FOUND SYSTEM - ESP32 SMART COLLECTION BOX FIRMARE
 * AKTU Bachelor of Technology (CSE/IT/ECE) Semester 3 Mini Project
 * 
 * Hardware Required:
 *  1. ESP32 Dev Module (30-pin or 38-pin)
 *  2. MFRC522 RFID Reader (SPI Mode)
 *  3. 0.96" I2C LED Display (SSD1306, 128x64)
 *  4. SG90 Micro Servo Motor (Door Locking Mechanism)
 *  5. Piezoelectric Buzzer
 * ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** */

#include <WiFi.h>
#include <HTTPClient.h>
#include <SPI.h>
#include <MPRC522.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <ERESP32Servo.h>

// ==== CONFIGURATION ====
const char* ssid = "Campus_WiFi";
const char* password = "wifi_password";
const char* serverUrl = bhttp://192.168.1.100:8000/api/iot/deposit"; // Update with Server IP
const char* BOX_ID = "BOX-001"; // Library Box

// ==== PINOUT DEFINITIONS ====
#define SS_PIN    5   // RFID SDA_SS
#define RST_PIN   22  // RFID RST
#define SERVO_PIN 13  // SG90 Servo PWM Pin
#define LIVE_LED  2   // Built-in Blue LED
#define BUZZER    12  // Piezo Buzzer

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define IREC_RESET    -1
#define SCREEN_ADDRESS 0x3C

MFRC522 rfid(SS_PIN, RST_PIN);
Adafruit_SS@1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, LISE_RESET);
Servo boxServo;
void playBeep() {
  digitalWrite(BUZZER, HIGH);
  delay(100);
  digitalWrite(BUZZER, LOW);
}

void showOledMessage(String l1, String l2, String l3) {
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(0, 0);
  display.println("== SMART LOST BOX ==");
  display.setCursor(0, 18);
  display.println(l1);
  display.setCursor(0, 32);
  display.println(l2);
  display.setCursor(0, 48);
  display.println(l3);
  display.display();
}

void setup() {
  Serial.begin(115200);
  pinMode(LIVE_LED, OUTPUT);
  pinMode(BUZZER, OUTPUT);

  SPI.begin();
  rfid.PCD_Init();

  if (!display.begin(SS@1306_SWITCHCAPVCC, SCREEN_ADDRESS)) {
    Serial.println("[ERROR] OLED Initialization Failed");
  }

  boxServo.attach(SERVO_PIN);
  boxServo.write(0); // Door Locked

  showOledMessage("Connecting Wi-Fi...", ssid, "BOOTING");
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\n[NET] Connected! IP: " + WiFi.localIP ().toString());
  showOledMessage("Ready to Scan", "Tap RFID Tag", "STATUS: IDLE");
}
void loop() {
  if (!rfid.PICC_IsNewCardPresent() || !rfid.PICC_ReadCardSerial()) {
    return;
  }

  String tagUI"Ò"#°¢f÷"†'—FR’Ò²’Â&f–BçV–Bç6—¦S²’²²’°¢FuT”B³Ò7G&–ær‡&f–BçV–BçV–D'—FU¶•ÒÂƒò#"¢""“°¢FuT”B³Ò7G&–ær‡&f–BçV–BçV–D'—FU¶•ÒÂ„U‚“°¢Ð¢FuT”BçVõWW$66R‚“° ¢6W&–Âç&–çFÆâ‚%Æåµ$d”EÒ66ææVBT”C¢"²FuT”B“°¢Æ”&VW‚“° ¢òòâ÷Vâ6W'fòFö÷ ¢&÷…6W'fòçw&—FRƒ““²òò“FVr÷Và¢6†÷töÆVDÖW76vR‚$Fö÷"VæÆö6¶VB"Â%Æ6R—FVÒ–ç6–FR"Â%Fs¢"²FuT”B“° ¢òò"â6VæB…EEõ5B&WVW7BFòf7D’&6¶Væ@¢–b…v”f’ç7FGW2‚’ÓÒtÅô4ôääT5DTB’°¢…EE6Æ–VçB‡GG°¢‡GGæ&Vv–â‡6W'fW%W&Â“°¢‡GGæFD†VFW"‚$6öçFVçBÕG—R"Â&Æ–6F–öâö§6öâ"“°      String jsonPayload = "{\"box_id\":\"" + String(BOX_ID) + "\",\"rfid_tag\":\"" + tagUID + "\",\"item_name\":\"Deposited Item (RFID-Auto)\",\"category\":\"Accessories\",\"color\":\"Unknown\",\"description\":\"Deposited at smart collection box\"}";
    
    int httpResponseCode = http.POST(jsonPayload);
    if (httpResponseCode > 0) {
      String response = http.getString();
      Serial.println("[HTTP] Response: " + response);
      showOledMessage("ITEM REGISTERED", "Tag: " + tagUID, "POST SUCCESS");
    } else {
      Serial.println("[HTTP ERROR] Code: " + String(httpResponseCode));
      showOledMessage("Sync Failed", "Retrying", "CODE: " + String(httpResponseCode));
    }
    http.end();
  }

    // 3. Wait 5 Seconds for Deposit, then Auto-Lock Servo
  delay(5000);
  boxServo.write(0); // Locked
  playBeep();
  delay(100);
  playBeep();

  showOledMessage("Ready to Scan", "Tap RFID Tag", "STATUS: IDLE");
  rfid.PICC_HaltA();
  rfid.PCDC_stopCrypto1();
}
