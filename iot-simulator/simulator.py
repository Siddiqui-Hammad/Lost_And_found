#!/usr/bin/env python3
"""
TRACE AI - IoT Smart Collection Box Simulator
----------------------------------------------
Simulates physical ESP32 + MFRC-522 RFID reader hardware by transmitting
standardized JSON payloads to the FastAPI backend over HTTP REST API.

Future hardware will send the EXACT same HTTP POST payload.
"""

import sys
import time
import datetime
import json
import requests

API_ENDPOINT = "http://127.0.0.1:8000/api/iot/items"
HEARTBEAT_ENDPOINT = "http://127.0.0.1:8000/api/iot/boxes/{box_id}/heartbeat"

SAMPLE_TAGS = [
    {
        "rfid_id": "RFID-1024",
        "name": "Black Leather Wallet",
        "category": "Wallet",
        "color": "Black",
        "brand": "Wildhorn",
        "description": "Black leather wallet containing college identity card found near library reading room."
    },
    {
        "rfid_id": "RFID-E204A1",
        "name": "Boat Wireless Earbuds",
        "category": "Electronics",
        "color": "White",
        "brand": "Boat",
        "description": "White wireless earbuds in a black silicone case."
    },
    {
        "rfid_id": "RFID-KEY-88",
        "name": "Bike Keys with Keychain",
        "category": "Keys",
        "color": "Silver",
        "brand": "Royal Enfield",
        "description": "Three motorcycle keys on a black leather strap."
    },
    {
        "rfid_id": "RFID-CALC-09",
        "name": "Scientific Calculator",
        "category": "Electronics",
        "color": "Black",
        "brand": "Casio",
        "description": "Casio FX-991EX ClassWiz calculator."
    }
]

BOXES = [
    {"box_id": "BOX-001", "name": "Central Library Smart Box", "location": "Library"},
    {"box_id": "BOX-002", "name": "Student Canteen Smart Box", "location": "Canteen"},
    {"box_id": "BOX-003", "name": "Main Entrance Smart Box", "location": "Main Gate"},
]

def print_banner():
    print("\n" + "="*60)
    print("      TRACE AI — ESP32 HARDWARE SIMULATOR v2.0")
    print("      Simulating MFRC522 RFID + SG90 Servo + OLED")
    print("="*60)
    print(f"Target API Endpoint: {API_ENDPOINT}\n")

def simulate_scan(box: dict, tag: dict):
    payload = {
        "box_id": box["box_id"],
        "rfid_id": tag["rfid_id"],
        "location": box["location"],
        "timestamp": datetime.datetime.now().isoformat(),
        "item_name": tag["name"],
        "category": tag["category"],
        "color": tag["color"],
        "brand": tag["brand"],
        "description": tag["description"]
    }

    print("\n[ESP32 FIRMWARE EMULATOR] ──────────────────────────")
    print(f"📡 [RFID] Tag Detected! UID: {tag['rfid_id']}")
    print(f"📟 [OLED] SSD1306: 'Tag Scanned: {tag['rfid_id']}'")
    print(f"🔊 [BUZZER] *Beep-Beep* (2000Hz, 150ms)")
    print(f"⚙️  [SERVO] SG90 Servo rotated to 90° (Door Unlocked)")
    print(f"🌐 [WIFI] Transmitting HTTP POST to {API_ENDPOINT}...")
    print(f"📦 [PAYLOAD] {json.dumps(payload, indent=2)}")

    try:
        start_time = time.time()
        resp = requests.post(API_ENDPOINT, json=payload, timeout=5)
        elapsed = round((time.time() - start_time) * 1000, 1)

        if resp.status_code == 200:
            data = resp.json()
            print(f"\n✅ [RESPONSE 200 OK] ({elapsed}ms)")
            print(f"   Item ID Assigned:  {data.get('item_id')}")
            print(f"   Status Message:    {data.get('message')}")
            if data.get("match_found"):
                print(f"   🧠 AI MATCH FOUND: {data.get('top_match_score')}% Match Confidence!")
            print("⚙️  [SERVO] Door auto-locked to 0° after 5s deposit.")
            print("────────────────────────────────────────────────────\n")
        else:
            print(f"\n❌ [ERROR {resp.status_code}] {resp.text}")
    except requests.exceptions.ConnectionError:
        print("\n❌ [CONNECTION FAILED] Backend server is not running at http://127.0.0.1:8000")
        print("   Please start the backend server with: python run.py\n")
    except Exception as e:
        print(f"\n❌ [EXCEPTION] {e}\n")

def main():
    print_banner()
    
    while True:
        print("\nSelect an Action:")
        print("1. 🏷️  Scan Demo RFID Tag (Wallet, Earbuds, Keys, Calculator)")
        print("2. ✍️  Custom RFID Scan (Enter Manual UID & Item)")
        print("3. 💓 Send IoT Box Heartbeat Ping")
        print("4. 🚪 Exit Simulator")
        
        choice = input("\nEnter choice (1-4): ").strip()

        if choice == "1":
            print("\nSelect Hardware Box:")
            for idx, b in enumerate(BOXES, 1):
                print(f"  {idx}. {b['box_id']} ({b['location']})")
            b_idx = int(input("Select Box (1-3): ") or 1) - 1
            selected_box = BOXES[max(0, min(b_idx, len(BOXES)-1))]

            print("\nSelect RFID Tag to Scan:")
            for idx, t in enumerate(SAMPLE_TAGS, 1):
                print(f"  {idx}. {t['rfid_id']} — {t['name']} ({t['color']}, {t['brand']})")
            t_idx = int(input("Select Tag (1-4): ") or 1) - 1
            selected_tag = SAMPLE_TAGS[max(0, min(t_idx, len(SAMPLE_TAGS)-1))]

            simulate_scan(selected_box, selected_tag)

        elif choice == "2":
            box_id = input("Box ID (e.g. BOX-001): ").strip() or "BOX-001"
            location = input("Location (e.g. Library): ").strip() or "Library"
            rfid = input("RFID Tag UID (e.g. A37B219C): ").strip() or "A37B219C"
            name = input("Item Name: ").strip() or "Found Object"
            category = input("Category (Electronics/Wallet/Keys/Bottle/etc): ").strip() or "Other"
            color = input("Color: ").strip() or "Black"
            desc = input("Description: ").strip() or "Custom item deposited in smart box."
            
            box = {"box_id": box_id, "location": location}
            tag = {"rfid_id": rfid, "name": name, "category": category, "color": color, "brand": "", "description": desc}
            simulate_scan(box, tag)

        elif choice == "3":
            box_id = input("Box ID for heartbeat (default BOX-001): ").strip() or "BOX-001"
            try:
                url = HEARTBEAT_ENDPOINT.format(box_id=box_id)
                res = requests.post(url, timeout=3)
                print(f"💓 Heartbeat Status: {res.status_code} - {res.text}")
            except Exception as e:
                print(f"❌ Heartbeat failed: {e}")

        elif choice == "4":
            print("Exiting IoT Hardware Simulator.")
            break
        else:
            print("Invalid option. Please try again.")

if __name__ == "__main__":
    main()
