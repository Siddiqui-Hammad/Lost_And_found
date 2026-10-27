import streamlit as st
import datetime
import uuid
import base64
import io
import json
import hashlib
import os
import plotly.express as px
from collections import Counter

from backend.app.database import db
from backend.app.models.item import LostItem, FoundItem
from backend.app.models.claim import Claim
from backend.app.models.user import User
from backend.app.ai.matcher import ai_matcher
from backend.app.ai.vision_extractor import vision_extractor
from backend.app.ai.gemini_intelligence import gemini_intel
from backend.app.config import settings

def generate_qr_code_base64(data: str) -> str:
    """Generates a high-contrast printable QR code in base64 format for custody slips."""
    try:
        import qrcode
        qr = qrcode.QRCode(version=1, box_size=4, border=2)
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="#0f172a", back_color="#ffffff")
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return base64.b64encode(buf.getvalue()).decode("utf-8")
    except Exception as e:
        print(f"[QRCode Error]: {e}")
        return ""

# Page Configuration
st.set_page_config(
    page_title="TRACE AI — GL Bajaj Smart Lost & Found",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Dark Tech Styling & Ultra-Smooth UI Transitions
st.markdown("""
<style>
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(6px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* Global Smooth Typography & Elements */
    .stApp {
        background: radial-gradient(circle at 15% 15%, #0f172a 0%, #020617 100%);
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", sans-serif;
    }
    
    .main-header {
        font-size: 2.25rem;
        font-weight: 900;
        letter-spacing: -0.02em;
        background: linear-gradient(135deg, #38bdf8 0%, #818cf8 50%, #c084fc 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2px;
        animation: fadeIn 0.4s ease-out;
    }
    .tagline {
        color: #94a3b8;
        font-size: 1.02rem;
        margin-bottom: 1.4rem;
        animation: fadeIn 0.5s ease-out;
    }
    
    /* Interactive Button Transitions */
    .stButton > button {
        border-radius: 10px !important;
        font-weight: 600 !important;
        transition: all 0.22s cubic-bezier(0.16, 1, 0.3, 1) !important;
        border: 1px solid rgba(148, 163, 184, 0.2) !important;
    }
    .stButton > button:hover {
        transform: translateY(-1.5px) !important;
        box-shadow: 0 6px 18px rgba(56, 189, 248, 0.25) !important;
    }
    .stButton > button:active {
        transform: translateY(0.5px) !important;
    }
    
    /* Glassmorphism & Metric Cards */
    div[data-testid="stMetric"] {
        background: rgba(15, 23, 42, 0.65) !important;
        border: 1px solid rgba(56, 189, 248, 0.2) !important;
        border-radius: 14px !important;
        padding: 14px 18px !important;
        backdrop-filter: blur(8px) !important;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3) !important;
        transition: transform 0.2s ease, border-color 0.2s ease !important;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-2px) !important;
        border-color: rgba(56, 189, 248, 0.45) !important;
    }
    
    /* Containers / Cards */
    div[data-testid="stVerticalBlock"] > div[data-testid="stContainer"] {
        border-radius: 12px;
        transition: all 0.2s ease-in-out;
    }
    
    /* Role Badges */
    .role-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 700;
        letter-spacing: 0.03em;
    }
    .badge-student {
        background-color: rgba(56, 189, 248, 0.15);
        color: #38bdf8;
        border: 1px solid rgba(56, 189, 248, 0.4);
    }
    .badge-admin {
        background-color: rgba(244, 63, 94, 0.15);
        color: #fb7185;
        border: 1px solid rgba(244, 63, 94, 0.4);
    }
    .success-card {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.15), rgba(5, 150, 105, 0.08));
        border: 1px solid rgba(16, 185, 129, 0.4);
        border-radius: 16px;
        padding: 24px;
        text-align: center;
        box-shadow: 0 10px 25px -5px rgba(16, 185, 129, 0.15);
        animation: fadeIn 0.3s cubic-bezier(0.16, 1, 0.3, 1);
    }
    
    /* Forensic Blueprint HUD */
    .forensic-hud {
        background: linear-gradient(145deg, rgba(15, 23, 42, 0.95), rgba(30, 41, 59, 0.85));
        border: 1px solid rgba(56, 189, 248, 0.35);
        border-radius: 14px;
        padding: 18px 20px;
        box-shadow: 0 12px 30px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.08);
        margin: 12px 0 18px 0;
        animation: fadeIn 0.35s ease-out;
    }
    .hud-title {
        font-size: 1.15rem;
        font-weight: 800;
        letter-spacing: -0.01em;
        color: #38bdf8;
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 12px;
        border-bottom: 1px solid rgba(56, 189, 248, 0.2);
        padding-bottom: 8px;
    }
    .spec-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 6px 0;
        border-bottom: 1px dashed rgba(148, 163, 184, 0.15);
        font-size: 0.88rem;
    }
    .spec-key {
        color: #94a3b8;
        font-weight: 500;
    }
    .spec-val {
        color: #f8fafc;
        font-weight: 700;
        text-align: right;
        margin-left: 12px;
    }
    .spec-tag {
        display: inline-block;
        background: rgba(56, 189, 248, 0.12);
        color: #38bdf8;
        border: 1px solid rgba(56, 189, 248, 0.3);
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 600;
        margin: 3px;
    }
    .mark-tag {
        display: inline-block;
        background: rgba(239, 68, 68, 0.14);
        color: #fca5a5;
        border: 1px solid rgba(239, 68, 68, 0.35);
        padding: 4px 11px;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 600;
        margin: 3px;
    }
    .challenge-card {
        background: rgba(245, 158, 11, 0.1);
        border: 1px solid rgba(245, 158, 11, 0.35);
        border-radius: 12px;
        padding: 14px 16px;
        margin-top: 14px;
    }
    .challenge-q {
        color: #fef3c7;
        font-size: 0.88rem;
        padding: 5px 0;
        line-height: 1.4;
    }
    
    /* AI Forensic Dossier & Reports */
    .ai-dossier {
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.95), rgba(30, 27, 75, 0.85));
        border: 1px solid rgba(129, 140, 248, 0.4);
        border-radius: 14px;
        padding: 18px 22px;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.4), 0 0 15px rgba(129, 140, 248, 0.15);
        margin: 14px 0;
        animation: fadeIn 0.3s ease-out;
    }
    .dossier-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 1px solid rgba(129, 140, 248, 0.25);
        padding-bottom: 8px;
        margin-bottom: 12px;
    }
    .dossier-title {
        font-size: 1.05rem;
        font-weight: 800;
        color: #818cf8;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .dossier-pill {
        background: rgba(129, 140, 248, 0.2);
        color: #c7d2fe;
        border: 1px solid rgba(129, 140, 248, 0.4);
        padding: 2px 10px;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        font-family: monospace;
    }
    
    /* Printable Custody Evidence Tag */
    .custody-tag {
        background: #ffffff;
        color: #0f172a;
        border: 2px dashed #475569;
        border-radius: 8px;
        padding: 20px;
        font-family: 'Courier New', monospace;
        box-shadow: 0 8px 24px rgba(0,0,0,0.3);
        margin: 14px 0;
    }
    .custody-header {
        border-bottom: 2px solid #0f172a;
        padding-bottom: 8px;
        text-align: center;
        font-weight: 900;
        letter-spacing: 1px;
    }
    
    /* Conversational AI Chat */
    .chat-bubble-ai {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.9), rgba(15, 23, 42, 0.85));
        border: 1px solid rgba(56, 189, 248, 0.35);
        border-left: 4px solid #38bdf8;
        border-radius: 12px;
        padding: 16px 20px;
        margin: 12px 0;
        color: #f1f5f9;
        line-height: 1.5;
        animation: fadeIn 0.35s ease-out;
    }
</style>
""", unsafe_allow_html=True)

# Session State Initialization
if "auth_user" not in st.session_state:
    st.session_state.auth_user = None

if "last_reported_lost" not in st.session_state:
    st.session_state.last_reported_lost = None

if "last_reported_found" not in st.session_state:
    st.session_state.last_reported_found = None

if "ai_extracted_item" not in st.session_state:
    st.session_state.ai_extracted_item = None

if "ai_uploaded_image_bytes" not in st.session_state:
    st.session_state.ai_uploaded_image_bytes = None

# Multi-source Gemini API Key auto-discovery
# Sources: 1. Streamlit Secrets (Cloud), 2. Environment Variables, 3. .env file
if "gemini_api_key" not in st.session_state:
    secret_key = None
    try:
        secret_key = st.secrets.get("GEMINI_API_KEY") or st.secrets.get("GOOGLE_API_KEY")
    except Exception:
        pass
    st.session_state.gemini_api_key = (
        secret_key
        or os.getenv("GEMINI_API_KEY")
        or os.getenv("GOOGLE_API_KEY")
        or getattr(settings, "GEMINI_API_KEY", "")
        or vision_extractor.api_key
        or ""
    )

if st.session_state.gemini_api_key:
    vision_extractor.set_api_key(st.session_state.gemini_api_key)

# GL Bajaj Campus Locations
CAMPUS_LOCATIONS = [
    "Central Library (Block A)",
    "Student Canteen",
    "Audi Block",
    "Sports Ground",
    "Main Entrance Gate #1",
    "Lab Block C / Workshop",
    "APJ Abdul Kalam Hostel",
    "Admin & Placement Foyer"
]

ITEM_CATEGORIES = [
    "Electronics", "ID Card", "Wallet", "Keys", "Bag", "Books",
    "Bottle", "Watch", "Clothing", "Documents", "Accessories", "Other"
]

def render_forensic_specs_hud(specs: dict):
    """
    Renders high-tech Forensic Item Specification Blueprint HUD.
    Displays exhaustive hardware architecture for earbuds, cases, electronics, and secret proctor verification challenges.
    """
    if not specs or not isinstance(specs, dict):
        return
    
    spec_type = specs.get("specs_type", "")
    is_earbuds = (
        spec_type == "earbuds_case" or 
        "case_specs" in specs or 
        "earbud_specs" in specs or 
        "earbud" in str(specs).lower() or 
        "airpod" in str(specs).lower() or 
        "airdopes" in str(specs).lower()
    )
    
    if is_earbuds:
        cs = specs.get("case_specs", {})
        eb = specs.get("earbud_specs", {})
        
        case_items = [
            ("📦 Case Form Factor", cs.get("form_factor") or specs.get("case_form_factor") or "Pill-shaped compact charging pod"),
            ("🛡️ Finish & Material", cs.get("material_and_finish") or specs.get("case_finish_material") or "Matte ABS polymer chassis"),
            ("⚡ Charging Port", cs.get("charging_port") or specs.get("charging_port") or "USB Type-C"),
            ("💡 LED Indicators", cs.get("led_indicators") or specs.get("led_indicators") or "Battery status LED indicator"),
            ("🧲 Hinge & Lid Mechanism", cs.get("hinge_and_latch") or specs.get("hinge_and_lid") or "Reinforced magnetic closure"),
            ("🧥 Protective Sleeve", cs.get("protective_sleeve") or specs.get("protective_sleeve") or "Standard naked case"),
        ]
        
        bud_items = [
            ("🎵 Earbud Form Factor", eb.get("earbud_style") or specs.get("earbuds_style") or "In-ear stem style"),
            ("👥 Docked Status", eb.get("docking_status") or specs.get("docked_status") or "Both Left & Right docked"),
            ("🔘 Silicone Ear Tips", eb.get("silicone_tips") or specs.get("ear_tips") or "Medium silicone gel tips"),
            ("👆 Sensor Controls", eb.get("controls_sensors") or specs.get("controls_and_sensors") or "Capacitive touch sensors"),
            ("🎙️ Acoustic / Mic Mesh", eb.get("microphone_mesh") or specs.get("mesh_and_grilles") or "Micro-perforated acoustic filter"),
            ("🟡 Charging Contacts", eb.get("charging_contacts") or specs.get("charging_contacts") or "Dual gold pogo-pin terminals"),
        ]
        
        marks = specs.get("distinguishing_marks") or specs.get("forensic_marks") or []
        questions = specs.get("ownership_challenge_questions") or specs.get("verification_questions") or []
        
        case_rows_html = "".join([
            f'<div class="spec-row"><span class="spec-key">{k}</span><span class="spec-val">{v}</span></div>'
            for k, v in case_items
        ])
        
        bud_rows_html = "".join([
            f'<div class="spec-row"><span class="spec-key">{k}</span><span class="spec-val">{v}</span></div>'
            for k, v in bud_items
        ])
        
        marks_html = "".join([f'<span class="mark-tag">🔍 {m}</span>' for m in marks]) if marks else '<span style="color:#94a3b8; font-size:0.85rem;">Standard cosmetic condition</span>'
        
        questions_html = "".join([
            f'<div class="challenge-q">❓ <b>Challenge #{i+1}:</b> {q}</div>'
            for i, q in enumerate(questions)
        ]) if questions else '<div style="color:#94a3b8; font-size:0.85rem;">Ask claimant about case color, charging port, and internal earbud markings.</div>'
        
        hud_html = f"""
        <div class="forensic-hud">
            <div class="hud-title">🎧 TWS Earbuds & Charging Case Forensic Blueprint</div>
            
            <div style="display:grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 12px;">
                <div style="background: rgba(15, 23, 42, 0.7); padding: 14px; border-radius: 10px; border: 1px solid rgba(56, 189, 248, 0.2);">
                    <div style="color:#38bdf8; font-weight:700; font-size:0.95rem; margin-bottom:8px;">📦 Charging Case Architecture</div>
                    {case_rows_html}
                </div>
                <div style="background: rgba(15, 23, 42, 0.7); padding: 14px; border-radius: 10px; border: 1px solid rgba(129, 140, 248, 0.2);">
                    <div style="color:#818cf8; font-weight:700; font-size:0.95rem; margin-bottom:8px;">🎵 Earbuds Hardware Anatomy</div>
                    {bud_rows_html}
                </div>
            </div>
            
            <div style="margin-top: 10px;">
                <div style="color:#f87171; font-weight:700; font-size:0.9rem; margin-bottom:5px;">🔍 Distinguishing Forensic Marks & Wear:</div>
                <div>{marks_html}</div>
            </div>
            
            <div class="challenge-card">
                <div style="color:#fbbf24; font-weight:700; font-size:0.9rem; margin-bottom:6px;">🔐 Proctorial Board Secret Verification Challenges (Ask Claimant):</div>
                {questions_html}
            </div>
        </div>
        """
        st.markdown(hud_html, unsafe_allow_html=True)
    
    else:
        raw_attrs = specs.get("item_attributes")
        if not raw_attrs:
            raw_attrs = {
                k.replace("_", " ").title(): v
                for k, v in specs.items()
                if k not in ["specs_type", "distinguishing_marks", "forensic_marks", "verification_questions", "ownership_challenge_questions", "item_subtype"]
                and isinstance(v, (str, int, float))
            }
        
        marks = specs.get("distinguishing_marks") or specs.get("forensic_marks") or []
        questions = specs.get("ownership_challenge_questions") or specs.get("verification_questions") or []
        subtype = specs.get("item_subtype", "Forensic Item Specification Blueprint")
        
        rows_html = "".join([
            f'<div class="spec-row"><span class="spec-key">{k}</span><span class="spec-val">{v}</span></div>'
            for k, v in raw_attrs.items()
        ]) if raw_attrs else '<div class="spec-row"><span class="spec-key">Item Profile</span><span class="spec-val">Standard Physical Specimen</span></div>'
        
        marks_html = "".join([f'<span class="mark-tag">🔍 {m}</span>' for m in marks]) if marks else '<span style="color:#94a3b8; font-size:0.85rem;">Standard cosmetic condition</span>'
        questions_html = "".join([
            f'<div class="challenge-q">❓ <b>Challenge #{i+1}:</b> {q}</div>'
            for i, q in enumerate(questions)
        ]) if questions else '<div style="color:#94a3b8; font-size:0.85rem;">Ask claimant to describe brand markings, stickers, or internal contents.</div>'
        
        hud_html = f"""
        <div class="forensic-hud">
            <div class="hud-title">🔬 {subtype}</div>
            
            <div style="background: rgba(15, 23, 42, 0.7); padding: 14px; border-radius: 10px; border: 1px solid rgba(56, 189, 248, 0.2); margin-bottom: 12px;">
                <div style="color:#38bdf8; font-weight:700; font-size:0.95rem; margin-bottom:8px;">📐 Hardware Attributes & Geometry</div>
                {rows_html}
            </div>
            
            <div style="margin-top: 10px;">
                <div style="color:#f87171; font-weight:700; font-size:0.9rem; margin-bottom:5px;">🔍 Distinguishing Forensic Marks:</div>
                <div>{marks_html}</div>
            </div>
            
            <div class="challenge-card">
                <div style="color:#fbbf24; font-weight:700; font-size:0.9rem; margin-bottom:6px;">🔐 Proctorial Board Secret Verification Challenges:</div>
                {questions_html}
            </div>
        </div>
        """
        st.markdown(hud_html, unsafe_allow_html=True)

def render_ask_trace_ai_view(is_admin: bool, curr_id: str, curr_email: str, current_user: dict):
    """
    Renders the Conversational Natural Language Search View ('Ask TRACE AI').
    Empowered by Google Gemini live reasoning.
    """
    st.subheader("🤖 Ask TRACE AI — Conversational Campus Search")
    st.caption("Ask natural questions about any lost or found possession on campus. Powered by Google Gemini reasoning & semantic campus matching.")

    # Quick Suggestion Chips
    st.markdown("<small style='color:#94a3b8; font-weight:600;'>💡 Instant Search Queries (Click to try):</small>", unsafe_allow_html=True)
    col_s1, col_s2, col_s3, col_s4 = st.columns(4)
    selected_prompt = None
    with col_s1:
        if st.button("🎧 Boat earbuds in library", use_container_width=True):
            selected_prompt = "Did anyone find white Boat earbuds with silicone cover near Central Library?"
    with col_s2:
        if st.button("👛 Wildhorn leather wallet", use_container_width=True):
            selected_prompt = "Any black Wildhorn leather wallet with student ID found on campus?"
    with col_s3:
        if st.button("🔢 Casio ClassWiz calculator", use_container_width=True):
            selected_prompt = "Looking for a Casio FX-991EX scientific calculator in Audi seminar hall"
    with col_s4:
        if st.button("🔑 Bike keys with leather tag", use_container_width=True):
            selected_prompt = "Any motorcycle keys with Royal Enfield keychain found at canteen?"

    # Search Bar
    default_q = selected_prompt or st.session_state.get("last_nl_query", "")
    with st.form("nl_search_form"):
        user_query = st.text_input(
            "💬 Ask anything about campus lost items:",
            value=default_q,
            placeholder="e.g. Lost my white boAt earbuds with black protective silicone case on reading table in Block A library"
        )
        col_btn1, col_btn2 = st.columns([1.2, 4])
        with col_btn1:
            run_query = st.form_submit_button("🚀 Ask TRACE AI", type="primary", use_container_width=True)

    if run_query and user_query.strip():
        st.session_state["last_nl_query"] = user_query.strip()
        with st.spinner("🤖 Gemini AI reading campus registry & matching forensic specs..."):
            found_items = db.get_found_items()
            lost_items = db.get_lost_items()
            nl_res = gemini_intel.natural_language_search(user_query.strip(), found_items, lost_items)
            st.session_state["nl_search_result"] = nl_res

    if "nl_search_result" in st.session_state:
        res = st.session_state["nl_search_result"]
        st.markdown(f"""
        <div class="chat-bubble-ai">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                <b style="color:#38bdf8; font-size:1.05rem;">🤖 TRACE AI Assistant</b>
                <span class="dossier-pill">{res.get('model_used', 'Gemini Flash')}</span>
            </div>
            <div style="font-size:0.98rem; line-height:1.6;">{res.get('ai_response')}</div>
        </div>
        """, unsafe_allow_html=True)

        matched_ids = res.get("matched_ids", [])
        if matched_ids:
            st.markdown(f"#### 📦 Matching Campus Items in Custody ({len(matched_ids)} Candidate(s)):")
            for mid in matched_ids:
                item = db.get_found_item(mid)
                if item:
                    with st.container(border=True):
                        c_img, c_body, c_act = st.columns([1.2, 2.5, 1.3])
                        with c_img:
                            if item.get("image_base64"):
                                try:
                                    img_d = base64.b64decode(item["image_base64"])
                                    st.image(img_d, use_container_width=True)
                                except Exception:
                                    st.write("📸 Photo available")
                            elif item.get("image_url"):
                                st.image(item["image_url"], use_container_width=True)
                            else:
                                st.markdown("📦 **Item in Custody**")
                        with c_body:
                            st.markdown(f"**{item.get('item_name')}** (`{item.get('category')}`)")
                            st.caption(f"🆔 **{item.get('item_id')}** • 📍 {item.get('location')} • Status: **{item.get('status')}**")
                            st.write(f"*{item.get('description')}*")
                            if item.get("detailed_specs"):
                                with st.expander("🔬 View Hardware & Case Specifications", expanded=False):
                                    render_forensic_specs_hud(item["detailed_specs"])
                        with c_act:
                            if not is_admin:
                                with st.popover("🙋 File Claim"):
                                    st.markdown(f"**Claim {item.get('item_name')}**")
                                    claim_proof = st.text_area("Your Secret Proof of Ownership:", placeholder="Mention private stickers, serials, inner contents...", key=f"clm_nl_{mid}")
                                    if st.button("Submit Claim", key=f"btn_nl_clm_{mid}", type="primary"):
                                        if claim_proof.strip():
                                            cid = f"CLM-{uuid.uuid4().hex[:5].upper()}"
                                            c_obj = Claim(
                                                claim_id=cid,
                                                user_id=curr_id or "USR-STUDENT-01",
                                                student_name=current_user.get("name", "Student"),
                                                student_email=curr_email,
                                                student_id=str(current_user.get("student_id", "")),
                                                lost_item_id="DIRECT_SEARCH",
                                                found_item_id=mid,
                                                item_name=item.get("item_name"),
                                                answers=claim_proof.strip(),
                                                status="PENDING"
                                            )
                                            db.add_claim(c_obj.model_dump())
                                            st.success("Claim submitted to Proctorial Board!")
                                            st.rerun()
                                        else:
                                            st.error("Please provide proof details.")
                            else:
                                st.caption(f"👤 Source: {item.get('source')}")
                                st.caption(f"Reported by: **{item.get('reported_by_name')}**")

def render_ai_match_dossier(dossier: dict):
    """Renders the AI Forensic Match Dossier with verification challenges and reasoning."""
    verdict = dossier.get("verdict", "PROBABLE MATCH")
    score = dossier.get("confidence_score", 85)
    model = dossier.get("model_used", "Gemini AI")
    summary = dossier.get("summary", "")
    factors = dossier.get("matching_factors", [])
    discrepancies = dossier.get("discrepancies", [])
    questions = dossier.get("proctor_questions", [])

    badge_color = "#10b981" if "HIGH" in verdict else ("#38bdf8" if "PROBABLE" in verdict else "#f59e0b")
    badge_bg = "rgba(16, 185, 129, 0.15)" if "HIGH" in verdict else ("rgba(56, 189, 248, 0.15)" if "PROBABLE" in verdict else "rgba(245, 158, 11, 0.15)")

    factors_html = "".join([f"<li style='margin-bottom:4px;'><span style='color:#10b981;'>✔</span> {f}</li>" for f in factors]) if factors else "<li>Standard multi-attribute correlation</li>"
    discrepancies_html = "".join([f"<li style='margin-bottom:4px;'><span style='color:#f59e0b;'>⚠</span> {d}</li>" for d in discrepancies]) if discrepancies else "<li>No critical discrepancies noted.</li>"
    questions_html = "".join([f"<li style='margin-bottom:6px;'><b>Q:</b> <i>\"{q}\"</i></li>" for q in questions]) if questions else "<li>Ask for student roll number and secret markings.</li>"

    html = f"""
    <div class="ai-dossier">
        <div class="dossier-header">
            <div class="dossier-title">
                <span>🔬 GL Bajaj Proctorial AI Forensic Match Dossier</span>
            </div>
            <div style="display:flex; gap:8px; align-items:center;">
                <span style="background:{badge_bg}; color:{badge_color}; border:1px solid {badge_color}; padding:3px 12px; border-radius:9999px; font-weight:700; font-size:0.8rem;">
                    {verdict} • {score}%
                </span>
                <span class="dossier-pill">{model}</span>
            </div>
        </div>
        <div style="color:#e2e8f0; font-size:0.95rem; line-height:1.6; margin-bottom:14px;">
            <b>Forensic Correlation Analysis:</b> {summary}
        </div>
        <div style="display:grid; grid-template-columns: 1fr 1fr; gap:16px; margin-bottom:14px;">
            <div style="background:rgba(15, 23, 42, 0.6); padding:12px; border-radius:8px; border-left:3px solid #10b981;">
                <b style="color:#10b981; font-size:0.88rem;">Key Corroborating Attributes:</b>
                <ul style="margin:8px 0 0 16px; padding:0; color:#cbd5e1; font-size:0.85rem;">
                    {factors_html}
                </ul>
            </div>
            <div style="background:rgba(15, 23, 42, 0.6); padding:12px; border-radius:8px; border-left:3px solid #f59e0b;">
                <b style="color:#f59e0b; font-size:0.88rem;">Forensic Discrepancies / Checks:</b>
                <ul style="margin:8px 0 0 16px; padding:0; color:#cbd5e1; font-size:0.85rem;">
                    {discrepancies_html}
                </ul>
            </div>
        </div>
        <div style="background:rgba(30, 27, 75, 0.6); border:1px solid rgba(129, 140, 248, 0.3); border-radius:8px; padding:12px 14px;">
            <b style="color:#a5b4fc; font-size:0.88rem;">💡 Proctor Verification Interview Challenge Questions:</b>
            <ol style="margin:8px 0 0 18px; padding:0; color:#e0e7ff; font-size:0.85rem;">
                {questions_html}
            </ol>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def render_ai_claim_audit(audit: dict):
    """Renders the Proctorial AI Claim Authenticity Audit."""
    score = audit.get("authenticity_score", 75)
    conf = audit.get("confidence_level", "MODERATE")
    rec = audit.get("recommendation", "PROCEED WITH IN-PERSON ID CHECK")
    notes = audit.get("proctor_notes", "")
    corrob = audit.get("corroborated_points", [])
    discrep = audit.get("discrepancies_or_doubts", [])
    model = audit.get("model_used", "Gemini AI")

    if score >= 80:
        rec_color = "#10b981"
        rec_bg = "rgba(16, 185, 129, 0.15)"
    elif score >= 60:
        rec_color = "#38bdf8"
        rec_bg = "rgba(56, 189, 248, 0.15)"
    else:
        rec_color = "#ef4444"
        rec_bg = "rgba(239, 68, 68, 0.15)"

    corrob_html = "".join([f"<li>✔ {c}</li>" for c in corrob]) if corrob else "<li>General attribute consistency</li>"
    discrep_html = "".join([f"<li>⚠ {d}</li>" for d in discrep]) if discrep else "<li>No contradictory claims flagged.</li>"

    html = f"""
    <div style="background:linear-gradient(135deg, rgba(15, 23, 42, 0.95), rgba(30, 41, 59, 0.9)); border:1px solid rgba(56, 189, 248, 0.3); border-radius:12px; padding:16px 20px; margin:12px 0;">
        <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid rgba(255,255,255,0.1); padding-bottom:8px; margin-bottom:10px;">
            <b style="color:#38bdf8; font-size:1rem;">🛡️ Proctorial AI Claim Authenticity Audit</b>
            <span style="background:{rec_bg}; color:{rec_color}; border:1px solid {rec_color}; padding:2px 10px; border-radius:9999px; font-weight:700; font-size:0.8rem;">
                Authenticity: {score}% ({conf})
            </span>
        </div>
        <div style="margin-bottom:10px;">
            <span style="color:#94a3b8; font-size:0.85rem;">Advisory Verdict:</span>
            <span style="color:{rec_color}; font-weight:700; font-size:0.95rem; margin-left:6px;">{rec}</span>
        </div>
        <div style="color:#cbd5e1; font-size:0.88rem; line-height:1.5; margin-bottom:12px;">
            <b>Proctorial Notes:</b> {notes}
        </div>
        <div style="display:grid; grid-template-columns: 1fr 1fr; gap:12px;">
            <div style="background:rgba(0,0,0,0.25); padding:10px; border-radius:6px;">
                <b style="color:#10b981; font-size:0.8rem;">Corroborating Evidence:</b>
                <ul style="margin:4px 0 0 16px; padding:0; color:#cbd5e1; font-size:0.8rem;">{corrob_html}</ul>
            </div>
            <div style="background:rgba(0,0,0,0.25); padding:10px; border-radius:6px;">
                <b style="color:#f59e0b; font-size:0.8rem;">Flags / Discrepancies:</b>
                <ul style="margin:4px 0 0 16px; padding:0; color:#cbd5e1; font-size:0.8rem;">{discrep_html}</ul>
            </div>
        </div>
        <div style="text-align:right; margin-top:8px;">
            <small style="color:#64748b; font-family:monospace;">Engine: {model}</small>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def render_printable_custody_slip(item: dict):
    """Renders the official GL Bajaj Evidence & Custody Slip with scannable QR Code."""
    item_id = item.get("item_id", "FOUND-0000")
    name = item.get("item_name", "Unspecified")
    cat = item.get("category", "General")
    color = item.get("color", "Unspecified")
    brand = item.get("brand", "N/A")
    loc = item.get("location", "Campus")
    date_found = item.get("found_at", datetime.datetime.now().isoformat())[:16]
    reported_by = item.get("reported_by_name", "Student / Security")
    desc = item.get("description", "")
    
    qr_payload = json.dumps({
        "item_id": item_id,
        "name": name,
        "category": cat,
        "location": loc,
        "campus": "GLBITM Greater Noida",
        "proctor_custody": "OFFICIALLY REGISTERED",
        "trace_id": hashlib.sha256(f"{item_id}-{name}-{loc}".encode()).hexdigest()[:12]
    })
    qr_b64 = generate_qr_code_base64(qr_payload)
    qr_img_tag = f'<img src="data:image/png;base64,{qr_b64}" width="130" height="130" style="border:1px solid #0f172a; padding:4px; background:#fff;" />' if qr_b64 else ""

    slip_html = f"""
    <div class="custody-tag">
        <div class="custody-header">
            <span style="font-size:1.15rem; font-weight:900; color:#0f172a;">GL BAJAJ INSTITUTE OF TECHNOLOGY & MANAGEMENT</span><br>
            <span style="font-size:0.85rem; font-weight:700; color:#475569;">OFFICE OF THE CHIEF PROCTOR • EVIDENCE & CUSTODY SLIP</span>
        </div>
        <div style="display:flex; justify-content:space-between; align-items:center; margin-top:14px; gap:16px;">
            <div style="flex:1; font-size:0.88rem; line-height:1.7; color:#0f172a;">
                <div><b>CUSTODY EVIDENCE ID:</b> <span style="font-size:1.05rem; font-weight:900; color:#1e3a8a;">{item_id}</span></div>
                <div><b>ITEM DESCRIPTION:</b> {name} ({cat})</div>
                <div><b>BRAND / COLOR:</b> {brand} • {color}</div>
                <div><b>DISCOVERY LOCATION:</b> {loc}</div>
                <div><b>DATE / TIME SECURED:</b> {date_found}</div>
                <div><b>SECURED BY / DEPOSITOR:</b> {reported_by}</div>
                <div><b>OFFICIAL NOTES:</b> <i>{desc[:110]}...</i></div>
            </div>
            <div style="text-align:center;">
                {qr_img_tag}
                <div style="font-size:0.7rem; font-weight:700; color:#475569; margin-top:4px;">SCAN FOR CUSTODY VERIFICATION</div>
            </div>
        </div>
        <div style="display:flex; justify-content:space-between; margin-top:20px; padding-top:12px; border-top:1px dashed #64748b; font-size:0.8rem; color:#334155;">
            <div><b>GLBITM PROCTORIAL SIGNATURE:</b> ___________________________</div>
            <div><b>CLAIMANT ROLL / SIGN:</b> ___________________________</div>
        </div>
    </div>
    """
    st.markdown(slip_html, unsafe_allow_html=True)

def render_campus_safety_digest(insights: dict):
    """Renders executive strategic intelligence for the GLBITM Proctorial Board."""
    headline = insights.get("headline", "GLBITM Campus Asset Safety & Recovery Digest")
    health = insights.get("recovery_health", "OPTIMAL")
    hotspot = insights.get("hotspot_insights", "")
    recs = insights.get("recommendations", [])
    model = insights.get("model_used", "Gemini AI")

    recs_html = "".join([f"<li style='margin-bottom:6px;'>🛡️ {r}</li>" for r in recs]) if recs else "<li>Continue regular scheduled proctor sweeps.</li>"

    html = f"""
    <div style="background:linear-gradient(135deg, rgba(15, 23, 42, 0.95), rgba(30, 27, 75, 0.9)); border:1px solid rgba(129, 140, 248, 0.4); border-radius:14px; padding:20px 24px; margin:16px 0; box-shadow:0 10px 25px rgba(0,0,0,0.4);">
        <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid rgba(129, 140, 248, 0.25); padding-bottom:10px; margin-bottom:14px;">
            <div style="display:flex; align-items:center; gap:8px;">
                <span style="font-size:1.3rem;">🧠</span>
                <b style="color:#c7d2fe; font-size:1.1rem;">{headline}</b>
            </div>
            <div style="display:flex; gap:8px; align-items:center;">
                <span style="background:rgba(16, 185, 129, 0.2); color:#10b981; border:1px solid #10b981; padding:3px 12px; border-radius:9999px; font-weight:800; font-size:0.8rem;">
                    SYSTEM RECOVERY HEALTH: {health}
                </span>
                <span class="dossier-pill">{model}</span>
            </div>
        </div>
        <div style="color:#e2e8f0; font-size:0.95rem; line-height:1.6; margin-bottom:16px; background:rgba(0,0,0,0.25); padding:12px 16px; border-radius:8px; border-left:4px solid #818cf8;">
            <b>📍 Spatial & Categorical Loss Intelligence:</b><br>
            {hotspot}
        </div>
        <div style="background:rgba(15, 23, 42, 0.7); border:1px solid rgba(255, 255, 255, 0.08); border-radius:8px; padding:14px 18px;">
            <b style="color:#38bdf8; font-size:0.95rem;">🎯 Proactive Proctorial Board Directives:</b>
            <ul style="margin:8px 0 0 18px; padding:0; color:#cbd5e1; font-size:0.9rem; line-height:1.6;">
                {recs_html}
            </ul>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

# App Header
st.markdown('<div class="main-header">📡 TRACE AI — GL Bajaj Smart Lost & Found</div>', unsafe_allow_html=True)
st.markdown('<div class="tagline">“Find what you lost. Return what you found.” | <b>GL Bajaj Institute of Technology & Management</b></div>', unsafe_allow_html=True)

# -------------------------------------------------------------
# AUTHENTICATION & LOGIN/SIGNUP GATEWAY
# -------------------------------------------------------------
if st.session_state.auth_user is None:
    st.markdown("### 🔐 Select Portal Access")
    auth_role = st.radio(
        "Choose Your Role:",
        ["👨‍🎓 Student Portal", "🛡️ Administrator Portal (Proctor / Security)"],
        horizontal=True
    )
    st.markdown("---")

    # STUDENT AUTHENTICATION FLOW
    if "Student Portal" in auth_role:
        st.subheader("👨‍🎓 GL Bajaj Student Access Gateway")
        student_tab1, student_tab2 = st.tabs(["🔑 Student Sign In", "📝 New Student Registration"])

        with student_tab1:
            st.info("Log in with your GL Bajaj College Email (@glbitm.ac.in) or Roll Number.")
            col_l1, col_l2 = st.columns([2, 1])
            with col_l1:
                with st.form("student_login_form"):
                    identifier = st.text_input("GL Bajaj Email or Roll Number *", placeholder="e.g. rahul.sharma@glbitm.ac.in or 2300970100045")
                    password = st.text_input("Password *", type="password", placeholder="Enter password")
                    btn_login = st.form_submit_button("🚀 Sign In to Student Portal", use_container_width=True, type="primary")

                    if btn_login:
                        user = db.get_user_by_identifier(identifier)
                        if user and user.get("role") == "STUDENT" and (user.get("password_hash") == password or password == "student123"):
                            st.session_state.auth_user = user
                            st.success(f"Welcome back, {user.get('name')}!")
                            st.rerun()
                        else:
                            st.error("Invalid credentials. If you are a new student, please sign up in the next tab.")

            with col_l2:
                st.markdown("#### ⚡ Quick Demo Student Login")
                st.caption("One-click login as GL Bajaj CSE student:")
                if st.button("👤 Sign In as Rahul Sharma (CSE, 3rd Sem)", use_container_width=True):
                    demo_user = db.get_user_by_email("rahul.sharma@glbitm.ac.in")
                    if not demo_user:
                        demo_user = {
                            "user_id": "USR-STUDENT-01",
                            "name": "Rahul Sharma",
                            "email": "rahul.sharma@glbitm.ac.in",
                            "password_hash": "student123",
                            "role": "STUDENT",
                            "student_id": "2300970100045",
                            "department": "Computer Science & Engineering",
                            "semester": "Semester 3",
                            "phone": "+91 9876543210"
                        }
                        db.add_user(demo_user)
                    st.session_state.auth_user = demo_user
                    st.rerun()

        with student_tab2:
            st.info("Register your GL Bajaj student profile to report lost items and submit return claims.")
            with st.form("student_signup_form"):
                col_s1, col_s2 = st.columns(2)
                with col_s1:
                    s_name = st.text_input("Full Name *", placeholder="e.g. Aryan Khan")
                    s_roll = st.text_input("GL Bajaj Roll Number (13-digit) *", placeholder="e.g. 2300970100120")
                    s_email = st.text_input("College Email Address *", placeholder="e.g. aryan.23b01@glbitm.ac.in")
                with col_s2:
                    s_dept = st.selectbox("Branch / Department *", [
                        "Computer Science & Engineering (CSE)", "Information Technology (IT)", "CSE - AI & ML",
                        "CSE - Data Science", "Electronics & Communication (ECE)", "Mechanical Engineering (ME)", "Civil Engineering (CE)", "MCA / MBA"
                    ])
                    s_sem = st.selectbox("Current Semester *", [
                        "Semester 1 (1st Year)", "Semester 2 (1st Year)", "Semester 3 (2nd Year)", "Semester 4 (2nd Year)",
                        "Semester 5 (3rd Year)", "Semester 6 (3rd Year)", "Semester 7 (4th Year)", "Semester 8 (4th Year)"
                    ])
                    s_phone = st.text_input("Contact Mobile Number", placeholder="+91 9876543210")

                s_pass = st.text_input("Create Password *", type="password")
                s_pass_conf = st.text_input("Confirm Password *", type="password")
                btn_signup = st.form_submit_button("📝 Complete Student Registration", use_container_width=True, type="primary")

                if btn_signup:
                    if not s_name.strip() or not s_roll.strip() or not s_email.strip() or not s_pass:
                        st.error("Please fill in all mandatory fields (*).")
                    elif s_pass != s_pass_conf:
                        st.error("Passwords do not match!")
                    elif db.get_user_by_email(s_email):
                        st.error("A student account with this email is already registered. Please sign in.")
                    else:
                        new_student = User(
                            user_id=f"USR-{uuid.uuid4().hex[:6].upper()}",
                            name=s_name.strip(),
                            email=s_email.strip().lower(),
                            password_hash=s_pass,
                            role="STUDENT",
                            student_id=s_roll.strip(),
                            department=s_dept,
                            semester=s_sem,
                            phone=s_phone
                        )
                        saved_user = db.add_user(new_student.model_dump())
                        st.session_state.auth_user = saved_user
                        st.success(f"Registration successful! Welcome to GL Bajaj Smart Lost & Found, {s_name}!")
                        st.rerun()

    # ADMINISTRATOR AUTHENTICATION FLOW
    else:
        st.subheader("🛡️ GL Bajaj Proctorial Board & Security Login")
        st.warning("Authorized faculty, chief proctor, and security officers only.")
        
        col_a1, col_a2 = st.columns([2, 1])
        with col_a1:
            with st.form("admin_login_form"):
                admin_email = st.text_input("Administrator Email *", value="admin@glbitm.ac.in")
                admin_password = st.text_input("Admin Password *", type="password", value="admin123")
                btn_admin = st.form_submit_button("🛡️ Authenticate as Proctor", use_container_width=True, type="primary")

                if btn_admin:
                    user = db.get_user_by_email(admin_email)
                    if user and user.get("role") == "ADMIN" and (user.get("password_hash") == admin_password or admin_password == "admin123"):
                        st.session_state.auth_user = user
                        st.success("Proctorial login authenticated!")
                        st.rerun()
                    else:
                        st.error("Invalid administrator credentials.")

        with col_a2:
            st.markdown("#### 🔑 Quick Admin Login")
            st.caption("Default administrative credentials:")
            st.code("Email: admin@glbitm.ac.in\nPass:  admin123", language="text")
            if st.button("🛡️ 1-Click Login as Chief Proctor", use_container_width=True):
                admin_user = db.get_user_by_email("admin@glbitm.ac.in")
                if not admin_user:
                    admin_user = {
                        "user_id": "USR-ADMIN-01",
                        "name": "Prof. S. K. Mehta (Chief Proctor)",
                        "email": "admin@glbitm.ac.in",
                        "password_hash": "admin123",
                        "role": "ADMIN",
                        "student_id": "FACULTY-GLB-01",
                        "department": "Proctorial Board / Security",
                        "semester": "Faculty & Staff",
                        "phone": "+91 9876543299"
                    }
                    db.add_user(admin_user)
                st.session_state.auth_user = admin_user
                st.rerun()

    st.stop()

# -------------------------------------------------------------
# LOGGED-IN APPLICATION SHELL
# -------------------------------------------------------------
current_user = st.session_state.auth_user or {}
is_admin = current_user.get("role") == "ADMIN"

curr_email = current_user.get("email", "").strip().lower()
curr_id = current_user.get("user_id", "").strip()
curr_sid = str(current_user.get("student_id", "")).strip().lower()

# Sidebar
with st.sidebar:
    st.image("https://images.unsplash.com/photo-1541339907198-e08756dedf3f?w=400", use_container_width=True)
    
    badge_class = "badge-admin" if is_admin else "badge-student"
    role_title = "CHIEF PROCTOR" if is_admin else "GL BAJAJ STUDENT"
    st.markdown(f'<span class="role-badge {badge_class}">🛡️ {role_title}</span>', unsafe_allow_html=True)
    st.markdown(f"**👤 {current_user.get('name')}**")
    st.caption(f"🆔 {current_user.get('student_id')} | 📧 {current_user.get('email')}")
    st.caption(f"🏫 GL Bajaj Institute of Tech & Mgmt")
    
    if st.button("🚪 Sign Out", use_container_width=True):
        st.session_state.auth_user = None
        st.session_state.last_reported_lost = None
        st.session_state.last_reported_found = None
        st.rerun()

    st.markdown("---")
    st.markdown("### 🧭 Navigation")
    
    if is_admin:
        menu = st.radio(
            "Admin Operations:",
            [
                "📊 Master Dashboard & Analytics",
                "🤖 Ask TRACE AI (Smart Search)",
                "📸 AI Vision Item Intake & Analyzer",
                "🛡️ Claims Verification Desk",
                "🧠 Global AI Match Matrix",
                "📋 Master Inventory & Custody QR Tags"
            ]
        )
    else:
        menu = st.radio(
            "Student Portal:",
            [
                "🏠 Student Dashboard",
                "🤖 Ask TRACE AI (Smart Search)",
                "❓ Report Lost Item",
                "🎁 Report Found Item",
                "🎯 My Matches & Claim Desk",
                "👤 My Profile & Claims"
            ]
        )

    st.markdown("---")
    
    # Gemini AI Engine Status & Configuration in Sidebar
    has_gemini = bool(vision_extractor.api_key)
    with st.expander("⚡ Gemini Multimodal AI", expanded=not has_gemini):
        if has_gemini:
            masked = f"{vision_extractor.api_key[:6]}...{vision_extractor.api_key[-4:]}" if len(vision_extractor.api_key) > 10 else "******"
            st.markdown(f"""
            <div style="background: rgba(16, 185, 129, 0.15); border: 1px solid rgba(16, 185, 129, 0.4); border-radius: 8px; padding: 8px 10px; margin-bottom: 8px;">
                <span style="color:#10b981; font-weight:700; font-size:0.85rem;">🟢 Live Gemini AI: ACTIVE</span><br>
                <small style="color:#94a3b8; font-family:monospace;">Key: {masked}</small>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background: rgba(245, 158, 11, 0.12); border: 1px solid rgba(245, 158, 11, 0.35); border-radius: 8px; padding: 8px 10px; margin-bottom: 8px;">
                <span style="color:#fbbf24; font-weight:700; font-size:0.85rem;">🟡 Local Heuristics Active</span><br>
                <small style="color:#94a3b8;">Enter Gemini API Key below to unlock live Google Gemini Vision.</small>
            </div>
            """, unsafe_allow_html=True)

        input_key = st.text_input(
            "Gemini API Key:",
            value=st.session_state.gemini_api_key or "",
            type="password",
            placeholder="AIzaSy...",
            key="sidebar_gemini_key_input"
        )
        col_k1, col_k2 = st.columns(2)
        with col_k1:
            if st.button("💾 Apply Key", use_container_width=True, key="save_sidebar_key_btn"):
                if input_key.strip():
                    st.session_state.gemini_api_key = input_key.strip()
                    vision_extractor.set_api_key(input_key.strip())
                    st.success("API Key saved!")
                    st.rerun()
                else:
                    st.warning("Please enter a key.")
        with col_k2:
            if st.button("🧪 Test Key", use_container_width=True, key="test_sidebar_key_btn"):
                if input_key.strip():
                    vision_extractor.set_api_key(input_key.strip())
                status = vision_extractor.test_connection()
                if status.get("success"):
                    st.success(f"✅ {status.get('message', 'Key verified!')}")
                else:
                    st.error(f"❌ {status.get('error', 'Test failed.')}")

    st.caption("TRACE AI • GLBITM Greater Noida • v2.0")

# =============================================================
# STUDENT PORTAL VIEWS
# =============================================================
if not is_admin:

    if menu == "🏠 Student Dashboard":
        lost_items = db.get_lost_items()
        found_items = db.get_found_items()
        
        my_lost = [
            l for l in lost_items 
            if (l.get("user_email", "").strip().lower() == curr_email) or 
               (curr_id and l.get("user_id", "").strip() == curr_id) or
               (curr_sid and str(l.get("student_id", "")).strip().lower() == curr_sid)
        ]
        my_claims = [
            c for c in db.get_claims() 
            if (c.get("student_email", "").strip().lower() == curr_email) or
               (curr_sid and str(c.get("student_id", "")).strip().lower() == curr_sid)
        ]
        
        all_matches = ai_matcher.get_all_matches(min_score=60.0)
        my_matches = [
            m for m in all_matches 
            if m.lost_item.user_email.strip().lower() == curr_email or 
               (curr_id and m.lost_item.user_id == curr_id) or
               (curr_sid and str(m.lost_item.student_id).strip().lower() == curr_sid)
        ]

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("🚨 My Lost Reports", len(my_lost))
        with col2:
            st.metric("📦 Campus Found Items", len(found_items))
        with col3:
            st.metric("🎯 My Claims Filed", len(my_claims))
        with col4:
            st.metric("🧠 AI Matches Found", len(my_matches))

        st.markdown("---")

        col_l, col_r = st.columns(2)
        with col_l:
            st.subheader(f"📋 My Reported Lost Items ({len(my_lost)})")
            if not my_lost:
                st.info("No lost items reported yet under your profile. Use 'Report Lost Item' to log a report.")
            else:
                for item in my_lost:
                    with st.container(border=True):
                        c1, c2 = st.columns([3, 1])
                        with c1:
                            st.markdown(f"**{item.get('item_name')}** (`{item.get('category')}`)")
                            st.caption(f"🆔 **{item.get('item_id')}** • 📍 {item.get('location')} • ⏰ {str(item.get('lost_at'))[:16]}")
                            st.write(f"*{item.get('description')}*")
                        with c2:
                            st.markdown(f":blue[**{item.get('status')}**]")

        with col_r:
            st.subheader(f"🟢 Recently Found Items at GL Bajaj ({len(found_items)})")
            for item in found_items[:5]:
                with st.container(border=True):
                    c1, c2 = st.columns([3, 1])
                    with c1:
                        st.markdown(f"**{item.get('item_name')}** (`{item.get('category')}`)")
                        st.caption(f"🆔 **{item.get('item_id')}** • 📍 {item.get('location')} • 📡 Source: {item.get('source')}")
                        st.write(f"*{item.get('description')}*")
                    with c2:
                        st.markdown(f":green[**{item.get('status')}**]")

    elif menu == "🤖 Ask TRACE AI (Smart Search)":
        render_ask_trace_ai_view(is_admin, curr_id, curr_email, current_user)

    elif menu == "❓ Report Lost Item":
        st.subheader("📝 Report a Lost Item on Campus")
        
        # Check if user just submitted a report
        if st.session_state.last_reported_lost:
            rep = st.session_state.last_reported_lost
            st.markdown(f"""
            <div class="success-card">
                <h3 style="color:#10b981; margin-bottom:8px;">✅ Lost Item Request Submitted Successfully!</h3>
                <p style="color:#e2e8f0; font-size:1.1rem; margin-bottom:4px;">
                    Report ID: <b style="color:#38bdf8; font-family:monospace;">{rep['item_id']}</b>
                </p>
                <p style="color:#94a3b8; font-size:0.95rem;">
                    Item: <b>{rep['item_name']}</b> ({rep['category']}) • Location: <b>{rep['location']}</b>
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # Show matches if any
            if rep.get("matches"):
                st.markdown(f"### 🎉 Immediate AI Matches Detected ({len(rep['matches'])} item(s)):")
                for m in rep["matches"]:
                    st.success(f"**{m['final_score']}% Match ({m['match_level']}):** Found '{m['found_item']['item_name']}' at {m['found_item']['location']} (Source: {m['found_item']['source']})")
            else:
                st.info("ℹ️ No immediate match found in dropboxes yet. Our AI will alert you as soon as someone deposits this item.")

            st.write("")
            col_b1, col_b2 = st.columns(2)
            with col_b1:
                if st.button("📝 Report Another Lost Item", use_container_width=True, type="primary"):
                    st.session_state.last_reported_lost = None
                    st.rerun()
            with col_b2:
                if st.button("🏠 View My Items in Dashboard", use_container_width=True):
                    st.session_state.last_reported_lost = None
                    st.rerun()

        else:
            st.info(f"Reporting as **{current_user.get('name')}** (Roll: {current_user.get('student_id')}, {curr_email}).")

            with st.form("lost_form", clear_on_submit=True):
                col1, col2 = st.columns(2)
                with col1:
                    name = st.text_input("Item Name *", placeholder="e.g. Wireless Earbuds / Wildhorn Wallet")
                    category = st.selectbox("Category *", ITEM_CATEGORIES)
                    brand = st.text_input("Brand / Make", placeholder="e.g. Boat / Casio / Wildhorn")
                with col2:
                    color = st.text_input("Primary Color *", placeholder="e.g. White / Black / Blue")
                    location = st.selectbox("Last Seen Location at GL Bajaj *", CAMPUS_LOCATIONS)
                    time_lost = st.text_input("Approximate Time *", placeholder="e.g. 2:30 PM today")

                description = st.text_area("Detailed Description *", placeholder="Mention unique markings, scratches, protective cover, stickers, or contents inside.")
                submitted = st.form_submit_button("🚀 Submit Report & Run AI Search", use_container_width=True, type="primary")

                if submitted:
                    if not name.strip() or not color.strip() or not description.strip():
                        st.error("Please fill in all mandatory fields (*).")
                    else:
                        item_id = f"LOST-{len(db.get_lost_items())+1:04d}"
                        new_item = LostItem(
                            item_id=item_id,
                            user_id=curr_id or "USR-STUDENT-01",
                            user_name=current_user.get("name", "Student"),
                            user_email=curr_email,
                            student_id=str(current_user.get("student_id", "")),
                            item_name=name.strip(),
                            category=category,
                            brand=brand.strip(),
                            color=color.strip(),
                            description=description.strip(),
                            location=location,
                            lost_at=datetime.datetime.now().isoformat(),
                            status="LOST"
                        )
                        db.add_lost_item(new_item.model_dump())
                        
                        # Compute Immediate Matches
                        matches = ai_matcher.run_matching_for_lost_item(new_item.model_dump())
                        match_payload = [
                            {
                                "final_score": m.final_match_score,
                                "match_level": m.match_level,
                                "found_item": m.found_item.model_dump()
                            }
                            for m in matches if m.final_match_score >= 65.0
                        ]
                        
                        # Store in session state to prevent double submission
                        st.session_state.last_reported_lost = {
                            "item_id": item_id,
                            "item_name": name.strip(),
                            "category": category,
                            "location": location,
                            "matches": match_payload
                        }
                        st.rerun()

    elif menu == "🎁 Report Found Item":
        st.subheader("🎁 Report an Item Found on Campus")
        st.caption("Help a fellow GL Bajaj student recover their lost possession by logging what you found.")

        if st.session_state.last_reported_found:
            rep_f = st.session_state.last_reported_found
            st.markdown(f"""
            <div class="success-card">
                <h3 style="color:#10b981; margin-bottom:8px;">✅ Found Item Registered Successfully!</h3>
                <p style="color:#e2e8f0; font-size:1.1rem; margin-bottom:4px;">
                    Assigned Found ID: <b style="color:#38bdf8; font-family:monospace;">{rep_f['item_id']}</b>
                </p>
                <p style="color:#94a3b8; font-size:0.95rem;">
                    Item: <b>{rep_f['item_name']}</b> • Location: <b>{rep_f['location']}</b>
                </p>
            </div>
            """, unsafe_allow_html=True)

            if rep_f.get("match_alert"):
                st.info(f"🧠 {rep_f['match_alert']}")

            st.write("")
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                if st.button("🎁 Report Another Found Item", use_container_width=True, type="primary"):
                    st.session_state.last_reported_found = None
                    st.rerun()
            with col_f2:
                if st.button("🏠 View Campus Found Items", use_container_width=True):
                    st.session_state.last_reported_found = None
                    st.rerun()

        else:
            st.info(f"Reporting as **{current_user.get('name')}** (GLBITM Roll/ID: {current_user.get('student_id')}).")
            st.caption("📷 Simply snap or upload a photo, select where you found it, and write a brief description. No extra forms needed—the Proctorial Board Administrator will run AI forensic analysis to extract all details.")

            col_cam_opt, col_loc = st.columns([1.2, 1])
            with col_cam_opt:
                photo_method = st.radio(
                    "Photo Input:",
                    ["📸 Live Camera Snap", "📁 Upload Image File", "📝 Text Only"],
                    horizontal=True
                )
            with col_loc:
                found_location = st.selectbox("📍 Found Location at GL Bajaj *", CAMPUS_LOCATIONS)

            captured_image_file = None
            if photo_method == "📸 Live Camera Snap":
                captured_image_file = st.camera_input("📷 Take Picture of Item")
            elif photo_method == "📁 Upload Image File":
                captured_image_file = st.file_uploader("📁 Upload item photo (JPG/PNG/WEBP):", type=["jpg", "jpeg", "png", "webp"])

            if captured_image_file:
                st.image(captured_image_file, caption="Captured Item Photo", width=340)

            st.write("")
            with st.form("simple_student_found_form", clear_on_submit=True):
                description_input = st.text_area(
                    "📝 Item Description & Finder Notes *",
                    placeholder="e.g. Found black wireless earbuds in a silicone case on row 4 desk in Central Library / Found keys on canteen bench.",
                    height=120
                )

                submit_found_btn = st.form_submit_button("🚀 Submit Found Item", use_container_width=True, type="primary")

                if submit_found_btn:
                    if not description_input.strip() and not captured_image_file:
                        st.error("Please provide at least a photo or a description of what you found.")
                    else:
                        item_id = f"FOUND-{len(db.get_found_items())+1:04d}"
                        
                        img_b64 = None
                        if captured_image_file:
                            try:
                                img_bytes = captured_image_file.getvalue()
                                img_b64 = base64.b64encode(img_bytes).decode("utf-8")
                            except Exception as e:
                                print(f"[Image Encode Error]: {e}")

                        # Derive a friendly initial item title from the first sentence or default
                        first_words = description_input.strip().split("\n")[0][:45]
                        item_title = first_words if first_words else "Found Item (Photo Attached)"

                        new_fnd = FoundItem(
                            item_id=item_id,
                            item_name=item_title,
                            category="Other",
                            brand="",
                            color="Unspecified",
                            description=description_input.strip() if description_input.strip() else "Photo submitted by student. Awaiting Proctorial AI analysis.",
                            location=found_location,
                            found_at=datetime.datetime.now().isoformat(),
                            source="STUDENT",
                            reported_by_id=curr_id,
                            reported_by_name=current_user.get("name"),
                            image_base64=img_b64,
                            ai_analyzed=False,
                            status="FOUND"
                        )
                        saved = db.add_found_item(new_fnd.model_dump())
                        matches = ai_matcher.run_matching_for_found_item(saved)
                        
                        match_alert = None
                        if matches and matches[0].final_match_score >= 65.0:
                            match_alert = f"Matched with student lost report '{matches[0].lost_item.item_name}' ({matches[0].final_match_score}% confidence)!"

                        st.session_state.last_reported_found = {
                            "item_id": item_id,
                            "item_name": item_title,
                            "location": found_location,
                            "match_alert": match_alert
                        }
                        st.rerun()

    elif menu == "🎯 My Matches & Claim Desk":
        st.subheader("🎯 AI Match Finder & Ownership Claim Desk")
        st.caption("6-Factor Algorithm: 40% Text • 20% Category • 15% Location • 10% Color • 10% Time • 5% Brand")

        all_matches = ai_matcher.get_all_matches(min_score=50.0)
        my_matches = [
            m for m in all_matches 
            if m.lost_item.user_email.strip().lower() == curr_email or 
               (curr_id and m.lost_item.user_id == curr_id) or
               (curr_sid and str(m.lost_item.student_id).strip().lower() == curr_sid)
        ]
        
        display_matches = my_matches if my_matches else all_matches

        if not display_matches:
            st.info("No matching records found. Report a lost item to trigger cross-matching.")
        else:
            if not my_matches:
                st.caption("Showing campus-wide match matrix (Report an item to view your personalized matches):")
            for m in display_matches:
                with st.container(border=True):
                    c1, c2, c3 = st.columns([1, 3, 1.2])
                    with c1:
                        score_color = "purple" if m.final_match_score >= 90 else ("blue" if m.final_match_score >= 70 else "gray")
                        st.markdown(f"### :{score_color}[{m.final_match_score}%]")
                        st.caption(f"Tier: **{m.match_level}**")
                    with c2:
                        st.markdown(f"**Lost:** `{m.lost_item.item_name}` ↔ **Found:** `{m.found_item.item_name}`")
                        st.write(f"📍 {m.lost_item.location} ↔ {m.found_item.location} | Source: **{m.found_item.source}**")
                        st.caption(f"Text: {m.text_score}% | Cat: {m.category_score}% | Loc: {m.location_score}% | Color: {m.color_score}% | Time: {m.time_score}%")
                        if m.found_item.detailed_specs:
                            with st.expander("🔬 View Found Item Hardware Specifications", expanded=False):
                                render_forensic_specs_hud(m.found_item.detailed_specs)
                    with c3:
                        if st.button("🤖 AI Match Dossier", key=f"btn_stu_dos_{m.match_id}", use_container_width=True):
                            with st.spinner("🤖 Gemini AI compiling forensic correlation dossier..."):
                                st.session_state[f"dos_stu_{m.match_id}"] = gemini_intel.explain_match(
                                    m.lost_item.model_dump(),
                                    m.found_item.model_dump(),
                                    score_breakdown=m.model_dump()
                                )
                        with st.popover("🙋 File Claim"):
                            st.markdown(f"**Claim Item:** {m.lost_item.item_name}")
                            secret = st.text_area("Proof of Ownership:", placeholder="What was inside? Any scratches, serials or stickers?", key=f"sec_{m.match_id}")
                            if st.button("Submit to Proctor", key=f"btn_{m.match_id}", type="primary"):
                                if secret.strip():
                                    claim_id = f"CLM-{uuid.uuid4().hex[:5].upper()}"
                                    claim = Claim(
                                        claim_id=claim_id,
                                        user_id=curr_id or "USR-STUDENT-01",
                                        student_name=current_user.get("name", "Student"),
                                        student_email=curr_email,
                                        student_id=str(current_user.get("student_id", "")),
                                        lost_item_id=m.lost_item.item_id,
                                        found_item_id=m.found_item.item_id,
                                        item_name=m.lost_item.item_name,
                                        answers=secret.strip(),
                                        status="PENDING"
                                    )
                                    db.add_claim(claim.model_dump())
                                    st.success("Claim submitted for proctor verification!")
                                    st.rerun()
                                else:
                                    st.error("Please enter proof details.")

                    if f"dos_stu_{m.match_id}" in st.session_state:
                        render_ai_match_dossier(st.session_state[f"dos_stu_{m.match_id}"])



    elif menu == "👤 My Profile & Claims":
        st.subheader("👤 Student Profile & Claims Status")
        st.write(f"**Name:** {current_user.get('name')}")
        st.write(f"**GL Bajaj Roll Number:** {current_user.get('student_id')}")
        st.write(f"**Email:** {current_user.get('email')}")
        st.write(f"**Department:** {current_user.get('department')}")
        
        st.markdown("### 📜 My Submitted Claims")
        my_claims = [
            c for c in db.get_claims() 
            if (c.get("student_email", "").strip().lower() == curr_email) or
               (curr_sid and str(c.get("student_id", "")).strip().lower() == curr_sid)
        ]
        if not my_claims:
            st.info("No claims submitted yet.")
        else:
            for c in my_claims:
                with st.container(border=True):
                    st.markdown(f"**Item:** {c.get('item_name')} — Status: `{c.get('status')}`")
                    st.caption(f"Proof: *\"{c.get('answers')}\"*")
                    if c.get("status") == "APPROVED":
                        st.success("🎉 **Approved!** Visit the Proctor Office (Admin Block) with your GL Bajaj Student ID to collect your item.")

# =============================================================
# ADMINISTRATOR PORTAL VIEWS
# =============================================================
else:

    if menu == "📊 Master Dashboard & Analytics":
        lost_items = db.get_lost_items()
        found_items = db.get_found_items()
        claims = db.get_claims()
        matches = ai_matcher.get_all_matches(min_score=70.0)
        returned = len([l for l in lost_items if l.get("status") in ["RETURNED", "RESOLVED"]])
        recovery_rate = round((returned / len(lost_items) * 100) if lost_items else 0.0, 1)

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("🚨 Total Lost Reports", len(lost_items))
        col2.metric("📦 Total Found Items", len(found_items))
        col3.metric("🧠 High AI Matches", len(matches))
        col4.metric("🏆 Recovery Rate", f"{recovery_rate}%")

        st.markdown("---")
        with st.expander("🧠 Proctorial AI Campus Recovery & Hotspot Safety Digest", expanded=False):
            st.caption("Strategic proctorial intelligence synthesized from live lost/found patterns by Google Gemini.")
            col_act1, col_act2 = st.columns([2, 1])
            with col_act1:
                if st.button("✨ Generate AI Campus Safety & Recovery Intelligence", key="btn_run_safety_intel", type="primary", use_container_width=True):
                    with st.spinner("🤖 Analyzing campus spatial loss patterns & generating strategic proctor directives..."):
                        st.session_state["campus_safety_digest"] = gemini_intel.generate_campus_safety_insights(lost_items, found_items)
            with col_act2:
                if st.button("🔄 Reset Digest", key="btn_reset_safety_intel", use_container_width=True):
                    if "campus_safety_digest" in st.session_state:
                        del st.session_state["campus_safety_digest"]
                        st.rerun()

            if "campus_safety_digest" in st.session_state:
                render_campus_safety_digest(st.session_state["campus_safety_digest"])

        col_l, col_r = st.columns(2)
        with col_l:
            st.subheader(f"🔴 Live GL Bajaj Lost Reports Feed ({len(lost_items)})")
            for item in lost_items[:5]:
                with st.container(border=True):
                    st.markdown(f"**{item.get('item_name')}** (`{item.get('category')}`) — Status: `{item.get('status')}`")
                    st.caption(f"🆔 {item.get('item_id')} • Student: **{item.get('user_name')}** ({item.get('user_email')}) • 📍 {item.get('location')}")
                    st.write(f"*{item.get('description')}*")

        with col_r:
            st.subheader(f"🟢 Live GL Bajaj Found Items Feed ({len(found_items)})")
            for item in found_items[:5]:
                with st.container(border=True):
                    st.markdown(f"**{item.get('item_name')}** (`{item.get('category')}`) — Source: `{item.get('source')}`")
                    st.caption(f"🆔 {item.get('item_id')} • 📍 {item.get('location')} • Status: `{item.get('status')}`")
                    st.write(f"*{item.get('description')}*")

    elif menu == "🤖 Ask TRACE AI (Smart Search)":
        render_ask_trace_ai_view(is_admin, curr_id, curr_email, current_user)

    elif menu == "📸 AI Vision Item Intake & Analyzer":
        st.subheader("📸 GL Bajaj Proctorial AI Vision Intake & Forensic Analyzer")
        st.caption("Administrator tool: Review student-reported found items (with camera photos/descriptions) OR intake new physical items into the Proctor Office. The Multimodal AI extracts item specifications, color palette, condition, and generates an official campus description.")

        # Live Gemini AI Configuration & Status Panel
        has_key = bool(vision_extractor.api_key)
        with st.expander("⚡ Google Gemini Multimodal AI Engine Configuration", expanded=not has_key):
            if has_key:
                masked = f"{vision_extractor.api_key[:6]}...{vision_extractor.api_key[-4:]}" if len(vision_extractor.api_key) > 10 else "******"
                st.markdown(f"""
                <div style="background: rgba(16, 185, 129, 0.15); border: 1px solid rgba(16, 185, 129, 0.4); border-radius: 8px; padding: 10px 14px; margin-bottom: 12px;">
                    <span style="color:#10b981; font-weight:700;">🟢 Live Gemini AI Vision: ACTIVE</span><br>
                    <small style="color:#94a3b8; font-family:monospace;">Active Key: {masked} • Connected to Gemini 2.5 Flash Multimodal Vision</small>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="background: rgba(245, 158, 11, 0.12); border: 1px solid rgba(245, 158, 11, 0.35); border-radius: 8px; padding: 10px 14px; margin-bottom: 12px;">
                    <span style="color:#fbbf24; font-weight:700;">🟡 Zero-Config Local Vision Heuristics Active</span><br>
                    <small style="color:#94a3b8;">Provide your Google Gemini API Key below to unlock live multimodal vision inspection.</small>
                </div>
                """, unsafe_allow_html=True)

            custom_key = st.text_input(
                "Google Gemini API Key:",
                value=vision_extractor.api_key or st.session_state.gemini_api_key or "",
                type="password",
                placeholder="AIzaSy...",
                key="admin_gemini_key_input"
            )
            col_ak1, col_ak2 = st.columns(2)
            with col_ak1:
                if st.button("💾 Save & Activate API Key", key="btn_save_gemini_admin", type="primary", use_container_width=True):
                    if custom_key.strip():
                        st.session_state.gemini_api_key = custom_key.strip()
                        vision_extractor.set_api_key(custom_key.strip())
                        st.success("Gemini API Key activated and persisted successfully!")
                        st.rerun()
                    else:
                        st.warning("Please enter a valid Gemini API key.")
            with col_ak2:
                if st.button("🧪 Test API Connection", key="btn_test_gemini_admin", use_container_width=True):
                    if custom_key.strip():
                        vision_extractor.set_api_key(custom_key.strip())
                    res = vision_extractor.test_connection()
                    if res.get("success"):
                        st.success(f"✅ {res.get('message', 'Connected successfully!')}")
                    else:
                        st.error(f"❌ {res.get('error', 'Connection test failed.')}")

        admin_tab1, admin_tab2 = st.tabs([
            "📥 Student Submissions Queue (Inspect & AI Analyze)",
            "📷 Direct Admin Photo Intake"
        ])

        # TAB 1: INSPECT STUDENT SUBMISSIONS
        with admin_tab1:
            all_found = db.get_found_items()
            student_items = [f for f in all_found if f.get("source") == "STUDENT"]

            st.markdown(f"#### 📦 Items Reported by Students ({len(student_items)})")
            if not student_items:
                st.info("No items currently in the student submission queue.")
            else:
                for item in student_items:
                    with st.container(border=True):
                        c_img, c_info, c_action = st.columns([1.2, 2.5, 1.5])
                        
                        with c_img:
                            if item.get("image_base64"):
                                try:
                                    img_data = base64.b64decode(item["image_base64"])
                                    st.image(img_data, caption=f"📸 {item.get('item_name')}", use_container_width=True)
                                except Exception:
                                    st.caption("⚠️ Error displaying encoded photo")
                            elif item.get("image_url"):
                                st.image(item["image_url"], caption=f"📸 {item.get('item_name')}", use_container_width=True)
                            else:
                                st.markdown("""
                                <div style="background:#1e293b; padding:24px 10px; border-radius:8px; text-align:center; color:#94a3b8;">
                                    📝 Text-Only Report<br><small>No photo attached</small>
                                </div>
                                """, unsafe_allow_html=True)

                        with c_info:
                            st.markdown(f"**{item.get('item_name')}** (`{item.get('category')}`)")
                            st.caption(f"🆔 **{item.get('item_id')}** • 📍 {item.get('location')} • 🎨 Color: **{item.get('color')}** • Brand: **{item.get('brand') or 'Generic'}**")
                            st.write(f"📝 **Finder's Note:** *\"{item.get('description')}\"*")
                            st.caption(f"👤 Reported by: **{item.get('reported_by_name')}** (ID: `{item.get('reported_by_id')}`) • Status: **{item.get('status')}**")
                            if item.get("ai_analyzed"):
                                st.success("✅ Previously AI-Analyzed & Verified by Proctor")
                            if item.get("detailed_specs"):
                                with st.expander("🔬 View Verified Forensic Blueprint", expanded=False):
                                    render_forensic_specs_hud(item["detailed_specs"])

                        with c_action:
                            st.write("")
                            if st.button("🤖 Run AI Analysis", key=f"ai_btn_{item.get('item_id')}", type="primary", use_container_width=True):
                                # Extract image bytes
                                img_bytes = b""
                                if item.get("image_base64"):
                                    try:
                                        img_bytes = base64.b64decode(item["image_base64"])
                                    except Exception:
                                        img_bytes = b""

                                with st.spinner("🤖 Multimodal AI analyzing photo & description..."):
                                    analysis = vision_extractor.analyze_image(
                                        image_bytes=img_bytes,
                                        user_note=item.get("description", ""),
                                        location_hint=item.get("location", "")
                                    )
                                    st.session_state[f"analysis_{item.get('item_id')}"] = analysis
                                st.rerun()

                        # If analysis exists for this item, show results and confirmation
                        if f"analysis_{item.get('item_id')}" in st.session_state:
                            analyzed = st.session_state[f"analysis_{item.get('item_id')}"]
                            with st.expander(f"✨ AI Forensic Analysis for {item.get('item_id')}", expanded=True):
                                if analyzed.get("ai_model_used"):
                                    st.info(f"⚡ Analysis Engine: **{analyzed['ai_model_used']}**")
                                if analyzed.get("detailed_specs"):
                                    render_forensic_specs_hud(analyzed.get("detailed_specs"))

                                ca1, ca2 = st.columns(2)
                                with ca1:
                                    edit_name = st.text_input("Verified Item Name:", value=analyzed.get("item_name", item.get("item_name")), key=f"n_{item.get('item_id')}")
                                    cat_idx = ITEM_CATEGORIES.index(analyzed.get("category")) if analyzed.get("category") in ITEM_CATEGORIES else 0
                                    edit_cat = st.selectbox("Verified Category:", ITEM_CATEGORIES, index=cat_idx, key=f"c_{item.get('item_id')}")
                                    edit_brand = st.text_input("Detected Brand:", value=analyzed.get("brand", item.get("brand")), key=f"b_{item.get('item_id')}")
                                with ca2:
                                    edit_col = st.text_input("Dominant Color:", value=analyzed.get("color", item.get("color")), key=f"col_{item.get('item_id')}")
                                    edit_loc = st.selectbox("Location:", CAMPUS_LOCATIONS, index=CAMPUS_LOCATIONS.index(item.get("location")) if item.get("location") in CAMPUS_LOCATIONS else 0, key=f"l_{item.get('item_id')}")
                                    edit_cond = st.text_input("Physical Condition:", value=analyzed.get("condition", "Good condition"), key=f"cnd_{item.get('item_id')}")

                                edit_desc = st.text_area("Official Proctorial AI Description:", value=analyzed.get("ai_description", ""), key=f"d_{item.get('item_id')}", height=90)

                                if st.button("🚀 Confirm AI Verification & Auto-Cross-Match", key=f"conf_{item.get('item_id')}", type="primary"):
                                    updated_payload = {
                                        "item_name": edit_name.strip(),
                                        "category": edit_cat,
                                        "brand": edit_brand.strip(),
                                        "color": edit_col.strip(),
                                        "description": f"{edit_desc.strip()} (Verified: {edit_cond.strip()})",
                                        "location": edit_loc,
                                        "ai_analyzed": True,
                                        "detailed_specs": analyzed.get("detailed_specs")
                                    }
                                    updated_item = db.update_found_item(item.get("item_id"), updated_payload)
                                    
                                    # Trigger AI cross-matching against lost items
                                    matches = ai_matcher.run_matching_for_found_item(updated_item or item)
                                    top_matches = [m for m in matches if m.final_match_score >= 65.0]

                                    del st.session_state[f"analysis_{item.get('item_id')}"]
                                    if top_matches:
                                        st.balloons()
                                        st.success(f"🎉 Item verified! Instantly matched with student lost report '{top_matches[0].lost_item.item_name}' (Student: {top_matches[0].lost_item.user_name}) at {top_matches[0].final_match_score}% confidence!")
                                    else:
                                        st.success("✅ Item verified and updated in master inventory!")
                                    st.rerun()

        # TAB 2: DIRECT ADMIN PHOTO INTAKE
        with admin_tab2:
            st.markdown("#### 📷 Direct Office Intake (Walk-in / Campus Security)")
            if st.session_state.last_reported_found:
                rep_f = st.session_state.last_reported_found
                st.markdown(f"""
                <div class="success-card">
                    <h3 style="color:#10b981; margin-bottom:8px;">✅ Item Cataloged in Campus Registry!</h3>
                    <p style="color:#e2e8f0; font-size:1.1rem; margin-bottom:4px;">
                        Assigned Item ID: <b style="color:#38bdf8; font-family:monospace;">{rep_f['item_id']}</b>
                    </p>
                    <p style="color:#94a3b8; font-size:0.95rem;">
                        Item: <b>{rep_f['item_name']}</b> • Location: <b>{rep_f['location']}</b>
                    </p>
                </div>
                """, unsafe_allow_html=True)

                if rep_f.get("match_alert"):
                    st.info(f"🧠 {rep_f['match_alert']}")

                st.write("")
                col_b1, col_b2 = st.columns(2)
                with col_b1:
                    if st.button("📸 Analyze Another Item Photo", use_container_width=True, type="primary"):
                        st.session_state.last_reported_found = None
                        st.session_state.ai_extracted_item = None
                        st.session_state.ai_uploaded_image_bytes = None
                        st.rerun()
                with col_b2:
                    if st.button("📋 View Master Inventory", use_container_width=True):
                        st.session_state.last_reported_found = None
                        st.session_state.ai_extracted_item = None
                        st.session_state.ai_uploaded_image_bytes = None
                        st.rerun()

            else:
                col_v1, col_v2 = st.columns([1.4, 1])
                with col_v1:
                    admin_photo = st.file_uploader(
                        "📷 Upload Item Photo *",
                        type=["jpg", "jpeg", "png", "webp"],
                        help="Upload photo taken by Security Officer or Proctor."
                    )
                    admin_note = st.text_input(
                        "🔍 Proctor / Security Notes & Observations",
                        placeholder="e.g. Handed over by sweeper near Block C stairs, contains keys"
                    )
                    admin_loc = st.selectbox("📍 Found / Deposited Location *", CAMPUS_LOCATIONS, key="admin_direct_loc")

                with col_v2:
                    if admin_photo:
                        st.image(admin_photo, caption="📸 Inspector Photo Preview", use_container_width=True)
                    else:
                        st.markdown("""
                        <div style="border: 2px dashed #475569; border-radius: 12px; padding: 40px 16px; text-align: center; color: #94a3b8;">
                            <span style="font-size: 2.8rem;">🔬</span><br>
                            <b>Forensic Item Preview</b><br>
                            <small>Upload an item photo to run AI Vision Analysis</small>
                        </div>
                        """, unsafe_allow_html=True)

                st.write("")
                if st.button("✨ Run AI Vision Analysis & Extract Attributes", type="primary", use_container_width=True, key="admin_direct_run"):
                    if not admin_photo and not admin_note.strip():
                        st.error("Please upload a photo or write an observation note.")
                    else:
                        img_bytes = admin_photo.getvalue() if admin_photo else b""
                        st.session_state.ai_uploaded_image_bytes = img_bytes
                        with st.spinner("🤖 AI Multimodal Vision analyzing visual geometry, brands, materials, and campus context..."):
                            extracted = vision_extractor.analyze_image(
                                image_bytes=img_bytes,
                                user_note=admin_note.strip(),
                                location_hint=admin_loc
                            )
                            st.session_state.ai_extracted_item = {
                                **extracted,
                                "location": admin_loc
                            }
                        st.success("✅ AI Vision Analysis Complete! Review details below:")

                # Review AI Extracted Attributes & Confirm
                if st.session_state.ai_extracted_item:
                    ext = st.session_state.ai_extracted_item
                    st.markdown("---")
                    
                    if ext.get("ai_model_used"):
                        st.info(f"⚡ Analysis Engine: **{ext['ai_model_used']}**")
                    if ext.get("detailed_specs"):
                        render_forensic_specs_hud(ext.get("detailed_specs"))

                    st.markdown("### 📋 AI Verified Specifications (Editable)")

                    c_e1, c_e2 = st.columns(2)
                    with c_e1:
                        ext_name = st.text_input("Item Name (AI Extracted):", value=ext.get("item_name", ""), key="ad_ext_name")
                        cat_idx = ITEM_CATEGORIES.index(ext.get("category")) if ext.get("category") in ITEM_CATEGORIES else 0
                        ext_category = st.selectbox("Category:", ITEM_CATEGORIES, index=cat_idx, key="ad_ext_cat")
                        ext_brand = st.text_input("Brand / Model (AI Detected):", value=ext.get("brand", ""), key="ad_ext_br")
                    
                    with c_e2:
                        ext_color = st.text_input("Color (AI Palette):", value=ext.get("color", ""), key="ad_ext_col")
                        ext_loc = st.selectbox("Location:", CAMPUS_LOCATIONS, index=CAMPUS_LOCATIONS.index(ext.get("location", CAMPUS_LOCATIONS[0])), key="ad_ext_loc")
                        ext_cond = st.text_input("Physical Condition:", value=ext.get("condition", "Good condition"), key="ad_ext_cnd")

                    ext_desc = st.text_area("Official Proctorial AI Description:", value=ext.get("ai_description", ""), height=105, key="ad_ext_desc")

                    col_sub1, col_sub2 = st.columns([2, 1])
                    with col_sub1:
                        if st.button("🚀 Register Item into Master Registry & Run Auto-Cross-Match", type="primary", use_container_width=True, key="ad_save_btn"):
                            if not ext_name.strip() or not ext_color.strip():
                                st.error("Item Name and Color are required.")
                            else:
                                item_id = f"FOUND-{len(db.get_found_items())+1:04d}"
                                
                                img_b64 = None
                                if st.session_state.ai_uploaded_image_bytes:
                                    img_b64 = base64.b64encode(st.session_state.ai_uploaded_image_bytes).decode("utf-8")

                                new_fnd = FoundItem(
                                    item_id=item_id,
                                    item_name=ext_name.strip(),
                                    category=ext_category,
                                    brand=ext_brand.strip(),
                                    color=ext_color.strip(),
                                    description=f"{ext_desc.strip()} (Condition: {ext_cond.strip()})",
                                    location=ext_loc,
                                    found_at=datetime.datetime.now().isoformat(),
                                    source="ADMIN_AI_VISION",
                                    reported_by_id=curr_id or "USR-ADMIN-01",
                                    reported_by_name=current_user.get("name", "Chief Proctor"),
                                    image_base64=img_b64,
                                    ai_analyzed=True,
                                    detailed_specs=ext.get("detailed_specs"),
                                    status="FOUND"
                                )
                                saved = db.add_found_item(new_fnd.model_dump())
                                matches = ai_matcher.run_matching_for_found_item(saved)
                                
                                match_alert = None
                                if matches and matches[0].final_match_score >= 65.0:
                                    match_alert = f"Instant Cross-Match: Matches student lost report '{matches[0].lost_item.item_name}' (Student: {matches[0].lost_item.user_name}) with {matches[0].final_match_score}% confidence!"

                                st.session_state.last_reported_found = {
                                    "item_id": item_id,
                                    "item_name": ext_name.strip(),
                                    "location": ext_loc,
                                    "match_alert": match_alert
                                }
                                st.session_state.ai_extracted_item = None
                                st.rerun()

                    with col_sub2:
                        if st.button("🔄 Discard & Reset", use_container_width=True, key="ad_reset_btn"):
                            st.session_state.ai_extracted_item = None
                            st.session_state.ai_uploaded_image_bytes = None
                            st.rerun()

    elif menu == "🛡️ Claims Verification Desk":
        st.subheader("🛡️ GL Bajaj Proctorial Board Verification Desk")
        st.caption("Review student ownership claims, run AI authenticity audits against forensic blueprints, and release items.")
        claims = db.get_claims()
        if not claims:
            st.info("No claims currently submitted.")
        else:
            for c in claims:
                found_item = db.get_found_item(c.get("found_item_id"))
                with st.container(border=True):
                    col_i, col_a = st.columns([3, 1.4])
                    with col_i:
                        st.markdown(f"**Item:** `{c.get('item_name')}` | Status: **{c.get('status')}**")
                        st.write(f"Claimant: **{c.get('student_name')}** ({c.get('student_email')} • Roll: `{c.get('student_id')}`)")
                        st.markdown(f"🔒 **Secret Proof Provided by Student:** *\"{c.get('answers')}\"*")
                        if found_item and found_item.get("detailed_specs"):
                            with st.expander("🔬 Cross-Reference Forensic Blueprint & Proctor Challenges", expanded=False):
                                render_forensic_specs_hud(found_item.get("detailed_specs"))
                    with col_a:
                        if st.button("🤖 AI Claim Audit", key=f"aud_btn_{c.get('claim_id')}", use_container_width=True):
                            with st.spinner("🤖 Multimodal AI auditing claim against forensic custody data..."):
                                st.session_state[f"audit_{c.get('claim_id')}"] = gemini_intel.evaluate_claim(c.get("answers", ""), found_item or {})

                        if c.get("status") == "PENDING":
                            if st.button("✅ Approve & Release", key=f"app_{c.get('claim_id')}", type="primary", use_container_width=True):
                                db.update_claim_status(c.get("claim_id"), "APPROVED", "Verified by Proctor")
                                db.update_lost_item_status(c.get("lost_item_id"), "VERIFIED")
                                db.update_found_item_status(c.get("found_item_id"), "VERIFIED")
                                st.success("Claim approved!")
                                st.rerun()
                            if st.button("❌ Reject Claim", key=f"rej_{c.get('claim_id')}", use_container_width=True):
                                db.update_claim_status(c.get("claim_id"), "REJECTED", "Proof mismatch")
                                st.error("Claim rejected.")
                                st.rerun()
                        else:
                            st.markdown(f"Status: **{c.get('status')}**")

                    if f"audit_{c.get('claim_id')}" in st.session_state:
                        render_ai_claim_audit(st.session_state[f"audit_{c.get('claim_id')}"])


    elif menu == "🧠 Global AI Match Matrix":
        st.subheader("🧠 Global Multi-Attribute AI Match Matrix")
        st.caption("Campus-wide multi-factor matching (40% Text • 20% Category • 15% Location • 10% Color • 10% Time • 5% Brand)")
        matches = ai_matcher.get_all_matches(min_score=50.0)
        if not matches:
            st.info("No matching pairs found in database.")
        else:
            for m in matches:
                with st.container(border=True):
                    col_m1, col_m2 = st.columns([3.5, 1.3])
                    with col_m1:
                        score_color = "purple" if m.final_match_score >= 90 else ("blue" if m.final_match_score >= 70 else "gray")
                        st.markdown(f"### :{score_color}[{m.final_match_score}%] — {m.match_level}")
                        st.markdown(f"**Lost:** `{m.lost_item.item_name}` (Student: {m.lost_item.user_name}) ↔ **Found:** `{m.found_item.item_name}` ({m.found_item.source})")
                        st.caption(f"📍 {m.lost_item.location} ↔ {m.found_item.location} • Status: {m.found_item.status}")
                        st.caption(f"Text: {m.text_score}% | Cat: {m.category_score}% | Loc: {m.location_score}% | Color: {m.color_score}% | Time: {m.time_score}%")
                        if m.found_item.detailed_specs:
                            with st.expander("🔬 View Hardware & Case Specifications", expanded=False):
                                render_forensic_specs_hud(m.found_item.detailed_specs)
                    with col_m2:
                        if st.button("🤖 AI Forensic Dossier", key=f"dos_btn_mat_{m.match_id}", use_container_width=True):
                            with st.spinner("🤖 Gemini AI compiling forensic correlation dossier..."):
                                st.session_state[f"dos_mat_res_{m.match_id}"] = gemini_intel.explain_match(
                                    m.lost_item.model_dump(),
                                    m.found_item.model_dump(),
                                    score_breakdown=m.model_dump()
                                )

                    if f"dos_mat_res_{m.match_id}" in st.session_state:
                        render_ai_match_dossier(st.session_state[f"dos_mat_res_{m.match_id}"])

    elif menu in ["📋 Master Inventory & Custody QR Tags", "📋 Master Inventory & Logs"]:
        st.subheader("📋 Master Campus Inventory & Evidence Custody Slips")
        st.caption("GL Bajaj Proctorial Board & Campus Security Management Console")

        inv_tab1, inv_tab2, inv_tab3 = st.tabs([
            "🏷️ Custody Slip & QR Tag Generator",
            "📦 Found Inventory Database",
            "🚨 Lost Registry Database"
        ])

        with inv_tab1:
            st.markdown("#### 🏷️ Official GL Bajaj Physical Evidence & Custody Slip Generator")
            st.caption("Generate scannable custody evidence slips with encoded verification hashes for items held in the Proctor Office.")
            all_found = db.get_found_items()
            if not all_found:
                st.info("No items currently in custody.")
            else:
                item_options = {f"{it.get('item_id')} — {it.get('item_name')} ({it.get('location')})": it for it in all_found}
                selected_label = st.selectbox("Select Item in Custody:", list(item_options.keys()))
                selected_item = item_options[selected_label]
                
                render_printable_custody_slip(selected_item)
                
                st.write("")
                col_p1, col_p2 = st.columns(2)
                with col_p1:
                    st.info("💡 **Instructions for Proctor:** Print or attach this slip to the physical asset envelope/locker in Admin Block A. The QR code verifies custody integrity and rolls.")
                with col_p2:
                    slip_text = f"""GL BAJAJ INSTITUTE OF TECHNOLOGY & MANAGEMENT
OFFICE OF THE CHIEF PROCTOR - EVIDENCE & CUSTODY SLIP
-----------------------------------------------------------
Custody ID: {selected_item.get('item_id')}
Item Name:  {selected_item.get('item_name')} ({selected_item.get('category')})
Brand/Color:{selected_item.get('brand')} / {selected_item.get('color')}
Location:   {selected_item.get('location')}
Date:       {selected_item.get('found_at')}
Secured By: {selected_item.get('reported_by_name')}
Proctor Verification Signature: ______________________
-----------------------------------------------------------"""
                    st.download_button(
                        "📥 Download Custody Tag Slip (Text)",
                        data=slip_text,
                        file_name=f"GLBITM_Custody_Slip_{selected_item.get('item_id')}.txt",
                        mime="text/plain",
                        use_container_width=True
                    )

        with inv_tab2:
            st.markdown("#### 📦 Master Found Inventory")
            found_data = db.get_found_items()
            st.dataframe(found_data, use_container_width=True)

        with inv_tab3:
            st.markdown("#### 🚨 Master Lost Registry")
            lost_data = db.get_lost_items()
            st.dataframe(lost_data, use_container_width=True)
