# TRACE AI — Future ESP32 Hardware Integration Guide

## Overview
The TRACE AI architecture is engineered with a **strict separation of concerns**. The frontend web applications and AI matching engines do not communicate directly with micro-controllers. Instead, both the software simulator and physical hardware interact with the exact same standardized REST API:

```
[Physical RFID Tag]
       │
       ▼
[MFRC-522 Reader]
       │ (SPI)
       ▼
[ESP32 Micro-controller]
       │ (Wi-Fi HTTP Client)
       ▼
[POST /api/iot/items]
       │
       ▼
[FastAPI Backend Engine]
       │
       ▼
[MongoDB Collections]
       │
       ▼
[AI Semantic Matching Engine]
```

---

## Hardware Operation Flow

1. **Idle State**:
   - OLED screen displays `STATUS: READY TO SCAN` and box location.
   - SG90 servo motor is held at `0°` (Door locked).
2. **Scan Event**:
   - User approaches the Smart Drop Box with a found item bearing an RFID sticker or tags an item.
   - User taps the tag against the MFRC-522 reader.
3. **Local Hardware Reaction**:
   - Active buzzer emits a dual confirmation chime (2000Hz, 150ms).
   - OLED updates to `TAG DETECTED: [UID] -> UNLOCKING DOOR`.
   - Servo rotates to `90°` (Door unlocked).
4. **Cloud / Network Transmission**:
   - ESP32 builds an HTTP POST JSON payload and sends it to `http://<server-ip>:8000/api/iot/items`.
5. **Auto-Lock**:
   - ESP32 waits 5 seconds for the user to deposit the item inside the container.
   - Servo rotates back to `0°` (Door securely locked).
   - Buzzer confirms completion and OLED returns to idle state.

---

## ESP32 Pseudocode (HTTP POST Transmission)

```cpp
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

void sendScanToBackend(String rfidUID, String boxId, String location) {
    if (WiFi.status() == WL_CONNECTED) {
        HTTPClient http;
        http.begin("http://192.168.1.100:8000/api/iot/items");
        http.addHeader("Content-Type", "application/json");

        StaticJsonDocument<200> doc;
        doc["box_id"] = boxId;
        doc["rfid_id"] = rfidUID;
        doc["location"] = location;

        String requestBody;
        serializeJson(doc, requestBody);

        int httpResponseCode = http.POST(requestBody);
        if (httpResponseCode == 200) {
            String response = http.getString();
            Serial.println("[TRACE AI] Server acknowledged deposit: " + response);
        }
        http.end();
    }
}
```
