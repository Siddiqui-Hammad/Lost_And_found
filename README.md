# AI + IoT Smart Lost & Found System

> **Next-Generation Campus Lost & Found Platform**  
> Tagline: *“Find what you lost. Return what you found.”*

---

## 🌟 Key Highlights

1. **👨‍🎓 Student Portal (Sign Up & Login)**:
   - **Student Sign Up**: Full registration with Name, Roll Number / Student ID, College Email, Branch/Department, Semester, Phone, and Password.
   - **Student Dashboard**: Report lost items, register found items, monitor real-time AI matches, test the IoT smart drop box, and submit secret ownership proof.

2. **🛡️ Administrator Portal (Dedicated Login)**:
   - Secure Admin Access for Faculty & Proctorial Board (`admin@campus.edu` / `admin123`).
   - **Claims Verification Desk**: Review secret proof submitted by claimants, approve/reject releases.
   - **Hardware Fleet Monitor**: Monitor ESP32 drop box statuses, IP addresses, and trigger remote servo unlocks.
   - **Master Analytics & Heatmap**: Category breakdown and loss hotspot detection.

3. **🧠 AI Semantic Matching Engine**:
   - 6-Factor Composite Weighted Algorithm:
     - **35%** TF-IDF Text & Semantic Description Similarity
     - **20%** Category Exact/Semantic Match
     - **15%** Color Match
     - **10%** Brand / Make Match
     - **10%** Location Proximity Match
     - **10%** Temporal Window Decay

4. **📟 Interactive Virtual IoT Smart Box Simulator**:
   - Emulates an ESP32 micro-controller with SSD1306 OLED display, MFRC-522 RFID reader, and SG90 servo motor.

5. **⚡ ESP32 Production Firmware**:
   - Ready-to-flash Arduino C++ firmware located in [`iot_firmware/esp32_smart_box.ino`](file:///C:/Users/Asus/.gemini/antigravity/scratch/smart-lost-and-found/iot_firmware/esp32_smart_box.ino).

---

## 🚀 Quick Launch (Localhost)

### Option 1: Streamlit Web UI (Cloud & Local)
```powershell
streamlit run app.py
```
👉 Opens `http://localhost:8501`

### Option 2: Full-Stack FastAPI + Simulator
```powershell
python run.py
```
👉 Opens `http://127.0.0.1:8000`

---

## 🔐 Default Credentials for Testing

- **Administrator**:
  - Email: `admin@campus.edu`
  - Password: `admin123`
- **Student Demo**:
  - Email: `rahul.sharma@campus.edu` or Roll No: `2300970100045`
  - Password: `student123`
