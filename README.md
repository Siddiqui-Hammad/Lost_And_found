# TRACE AI — Smart AI + IoT Lost & Found System

> **Tagline:** *“Find what you lost. Return what you found.”*  
> **Production Prototype:** College-Level Smart Campus AI + IoT Ecosystem

---

## 🌟 1. System Overview & Architecture

**TRACE AI** solves the chaotic campus lost-and-found problem by marrying a centralized web management platform with **AI-Powered Multi-Attribute Semantic Matching** and an **IoT-Enabled Smart Collection Box Fleet**.

### Core Architecture
```
  React + TypeScript Frontend           Simulated IoT Device / Physical ESP32
             │                                              │
             ▼                                              ▼
   FastAPI REST Backend ───────────────► Stable IoT API (POST /api/iot/items)
             │                                              │
             ▼                                              ▼
  MongoDB / DocumentDB ◄────────────────────────────────────┘
             │
             ▼
  AI Semantic Matching Engine (40% Text, 20% Cat, 15% Loc, 10% Color, 10% Time, 5% Brand)
             │
             ▼
  Real-Time In-App Notifications & Proctorial Verification Desk
```

---

## 🚀 2. Technology Stack

- **Frontend**: React 18, TypeScript, Vite, Tailwind CSS, Lucide Icons, Recharts, Axios
- **Cloud/Alternate Frontend**: Streamlit Cloud (`app.py`) for instantaneous 1-click sharing
- **Backend**: Python 3.10+, FastAPI, Pydantic v2, Uvicorn, PyJWT, Bcrypt
- **Database**: MongoDB (via PyMongo / Motor) with high-performance embedded DocumentDB persistence fallback
- **AI Matching Engine**: Pretrained SentenceTransformers (`all-MiniLM-L6-v2`) / TF-IDF Char N-Gram Subword Cosine Similarity + 6-Factor Multi-Attribute Composite Scorer + Modular Vision/CLIP interface
- **IoT Layer**: ESP32 NodeMCU-32S, MFRC-522 13.56MHz RFID, SSD1306 OLED, SG90 Micro Servo, Piezo Buzzer

---

## 📁 3. Project Structure

```
trace-ai/
├── frontend/
│   ├── src/
│   │   ├── components/       # StatusBadge, MatchScoreCard, MetricCard, Navbar
│   │   ├── pages/            # Student/Admin Dashboards, ReportLost, ReportFound, MatchMatrix, Claims, IoTMonitor
│   │   ├── context/          # AuthContext with JWT persistence
│   │   ├── services/         # Axios API service endpoints
│   │   └── types/            # TypeScript interfaces
│   ├── package.json
│   ├── vite.config.ts
│   └── tailwind.config.js
│
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI entrypoint
│   │   ├── config.py         # Configurable AI weights & database URIs
│   │   ├── database.py       # MongoDB client + DocumentDB fallback
│   │   ├── models/           # User, LostItem, FoundItem, Claim, IoTBox, MatchRecord
│   │   ├── schemas/          # Pydantic request & response validation schemas
│   │   ├── routes/           # Auth, Lost, Found, IoT, Matches, Claims, Admin, Analytics
│   │   ├── ai/               # Text embeddings, Multi-factor scoring, Matcher service
│   │   ├── iot/              # Hardware fleet manager & RFID event processor
│   │   └── utils/            # Password hashing, JWT tokens, Seed generator
│   ├── requirements.txt
│   └── .env.example
│
├── iot-simulator/
│   ├── simulator.py          # Standalone CLI & interactive hardware emulator
│   └── README.md             # Simulator operation guide
│
├── hardware/
│   ├── esp32/
│   │   ├── esp32_firmware.ino # Ready-to-flash Arduino C++ firmware
│   │   └── circuit_pinout.md  # BOM & SPI/I2C/PWM wiring guide
│   └── README.md             # Future hardware integration guide
│
├── app.py                    # Streamlit Cloud production app
├── run.py                    # Unified 1-click localhost launcher
├── start_fullstack.bat       # Windows 1-click FastAPI launcher
├── start_streamlit.bat       # Windows 1-click Streamlit launcher
└── README.md
```

---

## ⚡ 4. Quick Start & Execution

### Prerequisites
- Python 3.10+ (Anaconda or Standard Python)
- (Optional) MongoDB running on `localhost:27017` (The app automatically uses the zero-dependency embedded DocumentDB if MongoDB is not running)

### Option A: 1-Click Launch (Windows)
Double-click [`start_fullstack.bat`](file:///C:/Users/Asus/.gemini/antigravity/scratch/smart-lost-and-found/start_fullstack.bat) or [`start_streamlit.bat`](file:///C:/Users/Asus/.gemini/antigravity/scratch/smart-lost-and-found/start_streamlit.bat).

### Option B: Terminal Launch
```powershell
# 1. Install dependencies
pip install -r backend/requirements.txt

# 2. Start FastAPI Backend & Web App
python run.py
```
👉 Server boots at **`http://127.0.0.1:8000`** with interactive Swagger documentation at **`http://127.0.0.1:8000/docs`**.

### Option C: Streamlit Web UI (for Streamlit Cloud)
```powershell
streamlit run app.py
```
👉 Opens **`http://localhost:8501`**.

---

## 🕹️ 5. Running the IoT Hardware Simulator

In a separate terminal, execute:
```powershell
python iot-simulator/simulator.py
```
- Select Option **1** to scan demo RFID tags (`RFID-1024` for Wildhorn Wallet, `RFID-E204A1` for Boat Earbuds).
- It transmits an HTTP POST to `http://127.0.0.1:8000/api/iot/items` exactly like the future ESP32.

---

## 🔐 6. Demo Credentials

| Role | Email / Roll No | Password | Access Privileges |
|---|---|---|---|
| **Campus Admin / Proctor** | `admin@campus.edu` | `admin123` | Claims Verification Desk, IoT Box Fleet Telemetry, Master Analytics, Reset Demo |
| **Student (CSE)** | `rahul.sharma@campus.edu` *(Roll: 2300970100045)* | `student123` | Report Lost/Found, View AI Matches, Submit Ownership Claims, Test Simulator |
| **Student (IT)** | `priya.verma@campus.edu` *(Roll: 2300970100088)* | `student123` | Report Lost/Found, View Matches |

---

## 🧠 7. AI Multi-Factor Matching Algorithm

The matching engine computes a composite score normalized from 0 to 100:
$$\text{Final Score} = 0.40 \cdot S_{\text{text}} + 0.20 \cdot S_{\text{cat}} + 0.15 \cdot S_{\text{loc}} + 0.10 \cdot S_{\text{col}} + 0.10 \cdot S_{\text{time}} + 0.05 \cdot S_{\text{brand}}$$

- **90% – 100%**: **HIGH PROBABILITY**
- **70% – 89%**: **POSSIBLE MATCH**
- **< 70%**: **LOW PROBABILITY**

---

## 📡 8. Future ESP32 Hardware Integration

When the physical hardware is ready:
1. Open [`hardware/esp32/esp32_firmware.ino`](file:///C:/Users/Asus/.gemini/antigravity/scratch/smart-lost-and-found/hardware/esp32/esp32_firmware.ino) in Arduino IDE.
2. Configure your Wi-Fi SSID and Server IP:
   ```cpp
   const char* WIFI_SSID     = "Campus_WiFi";
   const char* WIFI_PASSWORD = "CampusPassword";
   const char* API_URL       = "http://192.168.1.100:8000/api/iot/items";
   ```
3. Connect components according to [`hardware/esp32/circuit_pinout.md`](file:///C:/Users/Asus/.gemini/antigravity/scratch/smart-lost-and-found/hardware/esp32/circuit_pinout.md).
4. Flash the ESP32. **No modifications are needed on the backend or frontend!**

---

## 📋 9. API Reference Summary

- `POST /api/auth/register` — Student profile registration with roll number
- `POST /api/auth/login` — JWT authentication
- `GET /api/lost-items` & `POST /api/lost-items` — Lost reports management
- `GET /api/found-items` & `POST /api/found-items` — Manual found items
- `POST /api/iot/items` — **Hardware & Simulator RFID scan receiver**
- `GET /api/matches` — AI semantic matrix cross-matches
- `POST /api/claims` — Submit secret ownership proof
- `POST /api/claims/{id}/review` — Proctor approval/rejection
- `GET /api/admin/dashboard` & `POST /api/admin/reset-demo-data` — Admin console & demo reset
