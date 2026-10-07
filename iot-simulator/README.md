# TRACE AI — IoT Smart Collection Box Simulator

## Overview
Because the physical ESP32 hardware may not be immediately available during software evaluation, this simulator acts as an **exact drop-in replacement**.

It sends the identical `POST /api/iot/items` JSON payload that the future ESP32 micro-controller with an MFRC-522 RFID reader will send over Wi-Fi.

---

## How to Run

1. Ensure the TRACE AI backend is running:
   ```bash
   python run.py
   ```
2. Open a separate terminal window and start the simulator:
   ```bash
   python iot-simulator/simulator.py
   ```
3. Follow the interactive menu:
   - Option 1: Scan pre-configured demo RFID tags (e.g. `RFID-1024` for Wildhorn Wallet).
   - Option 2: Enter a custom RFID UID and item description.
   - Option 3: Send an IoT Box heartbeat ping.

---

## API Contract Emulation

### Request:
```http
POST /api/iot/items HTTP/1.1
Host: 127.0.0.1:8000
Content-Type: application/json

{
  "box_id": "BOX-001",
  "rfid_id": "A37B219C",
  "location": "Library",
  "timestamp": "2026-10-07T12:30:00"
}
```

### Response:
```json
{
  "success": true,
  "item_id": "FOUND-0001",
  "message": "Item registered successfully via Smart Box.",
  "match_found": true,
  "top_match_score": 94.5
}
```
