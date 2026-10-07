import streamlit as st
import datetime
import uuid
import plotly.express as px
from collections import Counter

from backend.app.database import db
from backend.app.models.item import LostItem, FoundItem
from backend.app.models.claim import Claim
from backend.app.models.user import User
from backend.app.schemas.iot import IoTScanRequest
from backend.app.iot.event_handler import iot_event_handler
from backend.app.ai.matcher import ai_matcher
from backend.app.config import settings

# Page Configuration
st.set_page_config(
    page_title="TRACE AI — Smart Lost & Found System",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Dark Tech Styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 900;
        background: linear-gradient(90deg, #38bdf8, #818cf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
    }
    .tagline {
        color: #94a3b8;
        font-size: 1.05rem;
        margin-bottom: 1.5rem;
    }
    .oled-box {
        background-color: #050b14;
        color: #38bdf8;
        font-family: 'Courier New', monospace;
        border: 2px solid #334155;
        border-radius: 12px;
        padding: 16px;
        box-shadow: inset 0 0 15px rgba(56, 189, 248, 0.2);
    }
    .role-badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    .badge-student {
        background-color: rgba(56, 189, 248, 0.15);
        color: #38bdf8;
        border: 1px solid #0284c7;
    }
    .badge-admin {
        background-color: rgba(244, 63, 94, 0.15);
        color: #fb7185;
        border: 1px solid #e11d48;
    }
</style>
""", unsafe_allow_html=True)

# Authentication Session State
if "auth_user" not in st.session_state:
    st.session_state.auth_user = None

# App Banner
st.markdown('<div class="main-header">📡 TRACE AI — Smart Lost & Found System</div>', unsafe_allow_html=True)
st.markdown('<div class="tagline">“Find what you lost. Return what you found.” | <b>Smart Campus Ecosystem</b></div>', unsafe_allow_html=True)

# -------------------------------------------------------------
# AUTHENTICATION & LOGIN/SIGNUP GATEWAY
# -------------------------------------------------------------
if st.session_state.auth_user is None:
    st.markdown("### 🔐 Select Portal Access")
    auth_role = st.radio(
        "Choose Your Role:",
        ["👨‍🎓 Student Portal", "🛡️ Administrator Portal"],
        horizontal=True
    )
    st.markdown("---")

    # STUDENT AUTHENTICATION FLOW
    if auth_role == "👨‍🎓 Student Portal":
        st.subheader("👨‍🎓 Student Access Gateway")
        student_tab1, student_tab2 = st.tabs(["🔑 Student Sign In", "📝 New Student Sign Up"])

        with student_tab1:
            st.info("Log in using your registered College Email or Student Roll Number.")
            col_l1, col_l2 = st.columns([2, 1])
            with col_l1:
                with st.form("student_login_form"):
                    identifier = st.text_input("College Email or Roll Number *", placeholder="e.g. rahul.sharma@campus.edu or 2300970100045")
                    password = st.text_input("Password *", type="password", placeholder="Enter your password")
                    btn_login = st.form_submit_button("🚀 Sign In to Student Portal", use_container_width=True, type="primary")

                    if btn_login:
                        user = db.get_user_by_identifier(identifier)
                        if user and user.get("role") == "STUDENT" and user.get("password_hash") == password:
                            st.session_state.auth_user = user
                            st.success(f"Welcome back, {user.get('name')}!")
                            st.rerun()
                        else:
                            st.error("Invalid student credentials. Please verify or register.")

            with col_l2:
                st.markdown("#### ⚡ Quick Demo Student Login")
                st.caption("One-click login with pre-configured student profile:")
                if st.button("👤 Sign In as Rahul Sharma (CSE)", use_container_width=True):
                    demo_user = db.get_user_by_email("rahul.sharma@campus.edu")
                    st.session_state.auth_user = demo_user
                    st.rerun()

        with student_tab2:
            st.info("Register your student profile to report lost items and submit return claims.")
            with st.form("student_signup_form"):
                col_s1, col_s2 = st.columns(2)
                with col_s1:
                    s_name = st.text_input("Full Name *", placeholder="e.g. Aryan Khan")
                    s_roll = st.text_input("Student Roll Number / Enrollment ID *", placeholder="e.g. 2300970100120")
                    s_email = st.text_input("College Email Address *", placeholder="e.g. aryan.khan@campus.edu")
                with col_s2:
                    s_dept = st.selectbox("Branch / Department *", [
                        "Computer Science & Engineering", "Information Technology", "Electronics & Communication",
                        "Mechanical Engineering", "Civil Engineering", "Electrical Engineering", "Other"
                    ])
                    s_sem = st.selectbox("Current Semester / Year *", [
                        "Semester 1", "Semester 2", "Semester 3", "Semester 4", "Semester 5", "Semester 6", "Semester 7", "Semester 8"
                    ])
                    s_phone = st.text_input("Contact Mobile Number *", placeholder="+91 9876543210")

                s_pass = st.text_input("Create Password *", type="password")
                s_pass_conf = st.text_input("Confirm Password *", type="password")
                btn_signup = st.form_submit_button("📝 Complete Student Registration", use_container_width=True, type="primary")

                if btn_signup:
                    if not s_name or not s_roll or not s_email or not s_pass:
                        st.error("Please fill in all mandatory fields (*).")
                    elif s_pass != s_pass_conf:
                        st.error("Passwords do not match!")
                    elif db.get_user_by_email(s_email):
                        st.error("A student account with this email is already registered.")
                    else:
                        new_student = User(
                            user_id=f"USR-{uuid.uuid4().hex[:6].upper()}",
                            name=s_name,
                            email=s_email,
                            password_hash=s_pass,
                            role="STUDENT",
                            student_id=s_roll,
                            department=s_dept,
                            semester=s_sem,
                            phone=s_phone
                        )
                        saved_user = db.add_user(new_student.model_dump())
                        st.session_state.auth_user = saved_user
                        st.success(f"Registration successful! Welcome {s_name}!")
                        st.rerun()

    # ADMINISTRATOR AUTHENTICATION FLOW
    elif auth_role == "🛡️ Administrator Portal":
        st.subheader("🛡️ Campus Administrator & Proctor Login")
        st.warning("Authorized faculty and proctorial board members only.")
        
        col_a1, col_a2 = st.columns([2, 1])
        with col_a1:
            with st.form("admin_login_form"):
                admin_email = st.text_input("Administrator Email *", value="admin@campus.edu")
                admin_password = st.text_input("Admin Password *", type="password", value="admin123")
                btn_admin = st.form_submit_button("🛡️ Authenticate as Administrator", use_container_width=True, type="primary")

                if btn_admin:
                    user = db.get_user_by_email(admin_email)
                    if user and user.get("role") == "ADMIN" and (user.get("password_hash") == admin_password or admin_password == "admin123"):
                        st.session_state.auth_user = user
                        st.success("Administrator login authenticated!")
                        st.rerun()
                    else:
                        st.error("Invalid administrator credentials.")

        with col_a2:
            st.markdown("#### 🔑 Quick Admin Login")
            st.caption("Default admin credentials:")
            st.code("Email: admin@campus.edu\nPass:  admin123", language="text")
            if st.button("🛡️ 1-Click Login as Campus Admin", use_container_width=True):
                admin_user = db.get_user_by_email("admin@campus.edu")
                st.session_state.auth_user = admin_user
                st.rerun()

    st.stop()

# -------------------------------------------------------------
# LOGGED-IN SHELL & NAVIGATION
# -------------------------------------------------------------
current_user = st.session_state.auth_user
is_admin = current_user.get("role") == "ADMIN"

# Sidebar
with st.sidebar:
    st.image("https://images.unsplash.com/photo-1541339907198-e08756dedf3f?w=400", use_container_width=True)
    
    badge_class = "badge-admin" if is_admin else "badge-student"
    role_title = "CAMPUS ADMINISTRATOR" if is_admin else "STUDENT"
    st.markdown(f'<span class="role-badge {badge_class}">🛡️ {role_title}</span>', unsafe_allow_html=True)
    st.markdown(f"**👤 {current_user.get('name')}**")
    st.caption(f"🆔 {current_user.get('student_id')} | 📧 {current_user.get('email')}")
    
    if st.button("🚪 Sign Out", use_container_width=True):
        st.session_state.auth_user = None
        st.rerun()

    st.markdown("---")
    st.markdown("### 🧭 Navigation")
    
    if is_admin:
        menu = st.radio(
            "Admin Operations:",
            [
                "📊 Master Dashboard & Analytics",
                "🛡️ Claims Verification Desk",
                "📦 Smart Drop Box Fleet Monitor",
                "🧠 Global AI Match Matrix",
                "📋 Master Inventory & Logs"
            ]
        )
    else:
        menu = st.radio(
            "Student Portal:",
            [
                "🏠 Student Dashboard",
                "❓ Report Lost Item",
                "🎁 Report Found Item",
                "🎯 My Matches & Claim Desk",
                "📟 Virtual IoT Drop Box",
                "👤 My Profile & Claims"
            ]
        )

    st.markdown("---")
    st.caption("TRACE AI v2.0 • AI + IoT Production System")

# =============================================================
# STUDENT PORTAL VIEWS
# =============================================================
if not is_admin:

    if menu == "🏠 Student Dashboard":
        lost_items = db.get_lost_items()
        found_items = db.get_found_items()
        my_lost = [l for l in lost_items if l.get("user_email", "").lower() == current_user.get("email", "").lower()]
        my_claims = [c for c in db.get_claims() if c.get("student_email", "").lower() == current_user.get("email", "").lower()]
        my_matches = [m for m in ai_matcher.get_all_matches(min_score=70.0) if m.lost_item.user_email.lower() == current_user.get("email", "").lower()]

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
            st.subheader("📋 My Reported Lost Items")
            if not my_lost:
                st.info("No lost items reported yet. Use 'Report Lost Item' to submit a report.")
            else:
                for item in my_lost:
                    with st.container(border=True):
                        c1, c2 = st.columns([3, 1])
                        with c1:
                            st.markdown(f"**{item.get('item_name')}** (`{item.get('category')}`)")
                            st.caption(f"📍 {item.get('location')} • ⏰ {item.get('lost_at')}")
                            st.write(f"*{item.get('description')}*")
                        with c2:
                            st.markdown(f":blue[**{item.get('status')}**]")

        with col_r:
            st.subheader("🟢 Recently Found Items on Campus")
            for item in found_items[:4]:
                with st.container(border=True):
                    c1, c2 = st.columns([3, 1])
                    with c1:
                        st.markdown(f"**{item.get('item_name')}** (`{item.get('category')}`)")
                        st.caption(f"📍 {item.get('location')} • 📡 Source: {item.get('source')}")
                        st.write(f"*{item.get('description')}*")
                    with c2:
                        st.markdown(f":green[**{item.get('status')}**]")

    elif menu == "❓ Report Lost Item":
        st.subheader("📝 Report a Lost Item")
        st.info("The AI Matching Engine will cross-compare existing IoT Drop Box deposits immediately upon submission.")

        with st.form("lost_form"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Item Name *", placeholder="e.g. Wireless Earbuds")
                category = st.selectbox("Category *", ["Electronics", "ID Card", "Wallet", "Keys", "Bag", "Books", "Bottle", "Watch", "Other"])
                brand = st.text_input("Brand / Make", placeholder="e.g. Boat / Wildhorn")
            with col2:
                color = st.text_input("Primary Color *", placeholder="e.g. White / Black")
                location = st.selectbox("Last Seen Location *", ["Library", "Canteen", "Main Gate", "Admin Block", "Sports Complex", "Classroom Hall"])
                time_lost = st.text_input("Approximate Time *", placeholder="e.g. 2:30 PM")

            description = st.text_area("Detailed Description *", placeholder="Provide unique features, case details, markings, or inside contents.")
            submitted = st.form_submit_button("🚀 Submit & Trigger AI Match Engine", use_container_width=True, type="primary")

            if submitted:
                if not name or not color or not description:
                    st.error("Please fill in required fields (*).")
                else:
                    item_id = f"LOST-{len(db.get_lost_items())+1:04d}"
                    new_item = LostItem(
                        item_id=item_id,
                        user_id=current_user.get("user_id"),
                        user_name=current_user.get("name"),
                        user_email=current_user.get("email"),
                        student_id=current_user.get("student_id", ""),
                        item_name=name,
                        category=category,
                        brand=brand,
                        color=color,
                        description=description,
                        location=location,
                        lost_at=datetime.datetime.now().isoformat(),
                        status="LOST"
                    )
                    db.add_lost_item(new_item.model_dump())
                    st.success(f"✅ Lost report registered successfully with ID: **{item_id}**!")

                    # Run Immediate AI Matching
                    matches = ai_matcher.run_matching_for_lost_item(new_item.model_dump())
                    high_matches = [m for m in matches if m.final_match_score >= 70.0]
                    if high_matches:
                        st.balloons()
                        st.markdown(f"### 🎉 Immediate AI Matches Detected ({len(high_matches)} match(es)):")
                        for m in high_matches:
                            st.success(f"**{m.final_match_score}% Match ({m.match_level}):** Found '{m.found_item.item_name}' at {m.found_item.location} (Source: {m.found_item.source})")

    elif menu == "🎁 Report Found Item":
        st.subheader("📦 Report a Found Item (Manual Submission)")
        with st.form("found_form"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Item Name *", placeholder="e.g. Scientific Calculator")
                category = st.selectbox("Category *", ["Electronics", "ID Card", "Wallet", "Keys", "Bag", "Books", "Bottle", "Watch", "Other"])
                brand = st.text_input("Brand / Make", placeholder="e.g. Casio")
            with col2:
                color = st.text_input("Color *", placeholder="e.g. Black")
                location = st.selectbox("Found Location *", ["Library", "Canteen", "Main Gate", "Admin Block", "Sports Complex"])
                found_time = st.text_input("Found Time", placeholder="e.g. 12:30 PM")

            description = st.text_area("Detailed Description *", placeholder="Describe location, markings, condition, etc.")
            submitted = st.form_submit_button("✅ Register Found Item", use_container_width=True, type="primary")

            if submitted:
                if not name or not color or not description:
                    st.error("Please fill in required fields.")
                else:
                    item_id = f"FOUND-{len(db.get_found_items())+1:04d}"
                    new_fnd = FoundItem(
                        item_id=item_id,
                        item_name=name,
                        category=category,
                        brand=brand,
                        color=color,
                        description=description,
                        location=location,
                        found_at=datetime.datetime.now().isoformat(),
                        source="MANUAL",
                        reported_by_name=current_user.get("name"),
                        status="FOUND"
                    )
                    saved = db.add_found_item(new_fnd.model_dump())
                    matches = ai_matcher.run_matching_for_found_item(saved)
                    st.success(f"🎉 Thank you! Found item recorded with ID: **{item_id}**")
                    if matches and matches[0].final_match_score >= 70.0:
                        st.info(f"🧠 Matched with lost report '{matches[0].lost_item.item_name}' ({matches[0].final_match_score}% confidence)!")

    elif menu == "🎯 My Matches & Claim Desk":
        st.subheader("🎯 AI Match Finder & Ownership Claim Desk")
        st.caption("AI evaluates items with 6 weighted attributes: 40% Text • 20% Category • 15% Location • 10% Color • 10% Time • 5% Brand")

        all_matches = ai_matcher.get_all_matches(min_score=50.0)
        my_matches = [m for m in all_matches if m.lost_item.user_email.lower() == current_user.get("email", "").lower()]
        display_matches = my_matches if my_matches else all_matches

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
                    st.caption(f"Text: **{m.text_score}%** | Cat: **{m.category_score}%** | Loc: **{m.location_score}%** | Color: **{m.color_score}%** | Time: **{m.time_score}%**")
                with c3:
                    with st.popover("🙋 File Claim"):
                        st.markdown(f"**Claim Item:** {m.lost_item.item_name}")
                        secret = st.text_area("Proof of Ownership:", placeholder="What was inside? Any scratches, serials or stickers?", key=f"sec_{m.match_id}")
                        if st.button("Submit to Proctor", key=f"btn_{m.match_id}", type="primary"):
                            if secret.strip():
                                claim_id = f"CLM-{uuid.uuid4().hex[:5].upper()}"
                                claim = Claim(
                                    claim_id=claim_id,
                                    user_id=current_user.get("user_id"),
                                    student_name=current_user.get("name"),
                                    student_email=current_user.get("email"),
                                    student_id=current_user.get("student_id", ""),
                                    lost_item_id=m.lost_item.item_id,
                                    found_item_id=m.found_item.item_id,
                                    item_name=m.lost_item.item_name,
                                    answers=secret,
                                    status="PENDING"
                                )
                                db.add_claim(claim.model_dump())
                                st.success("Claim submitted for proctor verification!")
                            else:
                                st.error("Please enter proof details.")

    elif menu == "📟 Virtual IoT Drop Box":
        st.subheader("📟 Virtual ESP32 Hardware Simulator")
        st.caption("Emulates RFID scanning, SSD1306 OLED display, and SG90 servo door locks.")

        col_box, col_input = st.columns([3, 2])
        with col_box:
            st.markdown("""
            <div class="oled-box">
                <div style="display:flex; justify-content:space-between; border-bottom:1px solid #334155; padding-bottom:4px;">
                    <span>TRACE AI SMART BOX</span>
                    <span>ONLINE 📶</span>
                </div>
                <div style="font-size: 1.2rem; font-weight:bold; margin-top:12px; color:#e0f2fe;">
                    STATUS: READY TO SCAN
                </div>
                <div style="font-size: 0.9rem; color:#38bdf8; margin-top:4px;">
                    Tap RFID Tag & Deposit Item
                </div>
                <div style="border-top:1px solid #334155; margin-top:14px; padding-top:4px; display:flex; justify-content:space-between; font-size:0.75rem; color:#64748b;">
                    <span>SERVO: LOCKED (0°)</span>
                    <span>BOX-001 (Library)</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col_input:
            rfid_tag = st.selectbox("Select RFID Tag:", ["RFID-1024 (Wildhorn Wallet)", "RFID-E204A1 (Boat Earbuds)", "RFID-KEY-88 (Keys)", "RFID-CALC-09 (Calculator)"])
            box_choice = st.selectbox("Target Drop Box:", ["BOX-001 (Library)", "BOX-002 (Canteen)", "BOX-003 (Main Gate)"])
            
            if st.button("🏷️ Tap RFID & Deposit into Box", use_container_width=True, type="primary"):
                clean_rfid = rfid_tag.split()[0]
                clean_box = box_choice.split()[0]
                req = IoTScanRequest(box_id=clean_box, rfid_id=clean_rfid, location="Library" if "BOX-001" in clean_box else "Canteen")
                resp = iot_event_handler.process_scan(req)
                st.success(f"🎉 **DEPOSIT SUCCESSFUL!** Item ID: `{resp.item_id}`")
                if resp.match_found:
                    st.balloons()
                    st.markdown(f"🧠 **AI Match Triggered:** Matched with lost item at **{resp.top_match_score}% confidence**!")

    elif menu == "👤 My Profile & Claims":
        st.subheader("👤 Student Profile & Claims Status")
        st.write(f"**Name:** {current_user.get('name')}")
        st.write(f"**Roll Number:** {current_user.get('student_id')}")
        st.write(f"**Email:** {current_user.get('email')}")
        st.write(f"**Department:** {current_user.get('department')}")
        
        st.markdown("### 📜 My Submitted Claims")
        my_claims = [c for c in db.get_claims() if c.get("student_email") == current_user.get("email")]
        if not my_claims:
            st.info("No claims submitted yet.")
        else:
            for c in my_claims:
                with st.container(border=True):
                    st.markdown(f"**Item:** {c.get('item_name')} — Status: `{c.get('status')}`")
                    st.caption(f"Proof: *\"{c.get('answers')}\"*")

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

        col_c1, col_c2 = st.columns(2)
        with col_c1:
            st.markdown("#### 🥧 Category Distribution")
            cats = [l.get("category") for l in lost_items] + [f.get("category") for f in found_items]
            fig = px.pie(names=list(Counter(cats).keys()), values=list(Counter(cats).values()), hole=0.4)
            st.plotly_chart(fig, use_container_width=True)

        with col_c2:
            st.markdown("#### 📍 Loss Hotspots")
            locs = [l.get("location") for l in lost_items]
            fig = px.bar(x=list(Counter(locs).keys()), y=list(Counter(locs).values()), labels={'x': 'Location', 'y': 'Incidents'})
            st.plotly_chart(fig, use_container_width=True)

    elif menu == "🛡️ Claims Verification Desk":
        st.subheader("🛡️ Proctor & Faculty Verification Desk")
        claims = db.get_claims()
        for c in claims:
            with st.container(border=True):
                col_i, col_a = st.columns([3, 1.2])
                with col_i:
                    st.markdown(f"**Item:** `{c.get('item_name')}` | Status: **{c.get('status')}**")
                    st.write(f"Student: **{c.get('student_name')}** ({c.get('student_email')} • Roll: {c.get('student_id')})")
                    st.markdown(f"🔒 **Secret Proof:** *\"{c.get('answers')}\"*")
                with col_a:
                    if c.get("status") == "PENDING":
                        if st.button("✅ Approve & Release", key=f"app_{c.get('claim_id')}", type="primary"):
                            db.update_claim_status(c.get("claim_id"), "APPROVED", "Verified by Proctor")
                            db.update_lost_item_status(c.get("lost_item_id"), "VERIFIED")
                            db.update_found_item_status(c.get("found_item_id"), "VERIFIED")
                            st.success("Claim approved!")
                            st.rerun()
                        if st.button("❌ Reject Claim", key=f"rej_{c.get('claim_id')}"):
                            db.update_claim_status(c.get("claim_id"), "REJECTED", "Proof mismatch")
                            st.error("Claim rejected.")
                            st.rerun()
                    else:
                        st.markdown(f"Status: **{c.get('status')}**")

    elif menu == "📦 Smart Drop Box Fleet Monitor":
        st.subheader("📦 IoT Smart Drop Box Fleet Monitor")
        boxes = db.get_iot_boxes()
        st.dataframe(boxes, use_container_width=True)

    elif menu == "🧠 Global AI Match Matrix":
        st.subheader("🧠 Global Multi-Attribute AI Match Matrix")
        matches = ai_matcher.get_all_matches(min_score=50.0)
        for m in matches:
            with st.container(border=True):
                st.markdown(f"**{m.final_match_score}% ({m.match_level})**: Lost `{m.lost_item.item_name}` ↔ Found `{m.found_item.item_name}`")
                st.caption(f"Text: {m.text_score}% | Cat: {m.category_score}% | Loc: {m.location_score}% | Color: {m.color_score}% | Time: {m.time_score}%")

    elif menu == "📋 Master Inventory & Logs":
        st.subheader("📋 Master Campus Inventory")
        tab1, tab2 = st.tabs(["Found Inventory", "Lost Registry"])
        with tab1:
            st.dataframe(db.get_found_items(), use_container_width=True)
        with tab2:
            st.dataframe(db.get_lost_items(), use_container_width=True)
