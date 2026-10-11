# TRACE AI — Multimodal AI Campus Lost & Found System
### GL Bajaj Institute of Technology & Management (GLBITM) Edition

> **Tagline:** *“Find what you lost. Return what you found.”*  
> **Production Prototype:** College-Level Smart Campus AI Lost & Found Ecosystem

---

## 🌟 1. System Overview & Architecture

**TRACE AI** solves the chaotic campus lost-and-found problem by marrying a centralized web management platform with:
1. **Multimodal AI Vision Snap & Report**: When a student finds an item on campus, they don't have to fill out tedious forms—they simply take or upload a photo. The system automatically identifies the item, extracts attributes (name, category, brand, color, condition), and crafts an AI detailed description.
2. **AI-Powered Multi-Attribute Semantic Cross-Matching**: 6-factor composite algorithm computing semantic similarity, category match, location proximity, color harmony, time interval, and brand confidence.
3. **Dedicated Student vs Admin (Proctorial Board) Portals**: Distinct login/signup gateways tailored for GL Bajaj students and college administrative authorities.

### Core Architecture
```
  Student / Admin Web UI (Streamlit / React)
              │
              ▼
    FastAPI REST Backend ───────────────► POST /api/found-items/ai-analyze-photo
              │                                      │
              ▼                                      ▼
   MongoDB / DocumentDB Engine              Google Gemini 2.5 / Local Vision Engine
              │                                      │
              ▼                                      ▼
   AI Semantic Matching Engine ◄─────────────────────┘
   (40% Text, 20% Cat, 15% Loc, 10% Color, 10% Time, 5% Brand)
              │
              ▼
   Automated Match Alerts & Proctorial Claims Verification Desk
```

---

## 🚀 2. Technology Stack

- **Cloud/Web Frontend**: Streamlit Cloud (`app.py`, `streamlit_app.py`) for instantaneous 1-click sharing
- **Alternate Frontend**: React 18, TypeScript, Vite, Tailwind CSS, Lucide Icons
- **Backend**: Python 3.10+, FastAPI, Pydantic v2, Uvicorn, PyJWT, Bcrypt
- **Database**: MongoDB with high-performance embedded DocumentDB persistence fallback
- **Computer Vision & Multimodal AI**:
  - Google Gemini Multimodal Vision API (`google-genai` / `gemini-2.5-flash`)
  - Intelligent Local Color Palette & CV Engine (PIL dominant color quantization fallback)
- **AI Matching Engine**: Pretrained SentenceTransformers (`all-MiniLM-L6-v2`) / TF-IDF Char N-Gram Subword Cosine Similarity + 6-Factor Multi-Attribute Composite Scorer

---

## 📁 3. Project Structure

```
trace-ai/
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI entrypoint
│   │   ├── config.py         # Configurable AI weights & database settings
│   │   ├── database.py       # MongoDB client + DocumentDB fallback
│   │   ├── models/           # User, LostItem, FoundItem, Claim, MatchRecord
│   │   ├── schemas/          # Pydantic request & response validation schemas
│   │   ├── routes/           # Auth, Lost, Found, Matches, Claims, Admin, Analytics
│   │   ├── ai/
│   │   │   ├── matcher.py    # 6-Factor Multi-Attribute AI Matcher
│   │   │   └── vision_extractor.py # Multimodal Vision Photo Extractor
│   │   └── utils/            # Password hashing, JWT tokens, GL Bajaj Seed generator
│   └── requirements.txt
│
├── frontend/                 # Optional React + Vite UI
├── app.py                    # Streamlit Cloud production app
├── streamlit_app.py          # Streamlit Cloud entrypoint mirror
├── run.py                    # Unified 1-click localhost launcher
├── start_streamlit.bat       # Windows 1-click Streamlit launcher
├── requirements.txt          # Python deployment dependencies
└── README.md
```

---

## ⚡ 4. Quick Start & Execution

### Prerequisites
- Python 3.10+ (Anaconda or Standard Python)

### 1-Click Launch (Windows)
Double-click [`start_streamlit.bat`](file:///C:/Users/Asus/.gemini/antigravity/scratch/smart-lost-and-found/start_streamlit.bat).

### Terminal Launch
```powershell
pip install -r requirements.txt
streamlit run app.py
```

---

## 👥 5. User Roles & Credentials

### 👨‍🎓 Student Portal
- **Login / Signup**: Students can sign up with their GL Bajaj Roll Number, college email (`@glbitm.ac.in`), and department.
- **Demo Student**:
  - Email: `rahul.sharma@glbitm.ac.in`
  - Password: `student123`
  - Roll No: `2300970100045`

### 🛡️ Administrator Portal (Proctorial Board / Security)
- **Login**: Chief Proctor & Campus Security Staff.
- **Admin**:
  - Email: `admin@glbitm.ac.in`
  - Password: `admin123`
  - Department: Proctorial Board / Security
