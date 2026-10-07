import streamlit as st
import datetime
import uuid
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter

from backend.app.database import db
from backend.app.models import User, LostItem, FoundItem, Claim, IoTDepositRequest
from backend.app.ai_matcher import compute_match_score
from backend.app.config import settings

# Page Config
st.set_page_config(
    page_title="AI + IoT Smart Lost & Found System",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(90deg, #3b82f6, #10b981);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
    }
    .tagline {
        color: #94a3b8;
        font-size: 1.05rem;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 16px;
        text-align: center;
    }
    .oled-box {
        background-color: #050b14;
        color: #38bdf8;
        font-family: 'Courier New', monospace;
        border: 3px solid #334155;
        border-radius: 12px;
        padding: 14px;
        box-shadow: inset 0 0 10px rgba(56, 189, 248, 0.3);
    }
    .role-badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    .badge-student {
        background-color: rgba(59, 130, 246, 0.2);
        color: #60a5fa;
        border: 1px solid #3b82f6;
    }
    .badge-admin {
        background-color: rgba(239, 68, 68, 0.2);
        color: #f87171;
        border: 1px solid #ef4444;
    }
</style>
""", unsafe_allow_html=True)

# Session State Initialization for Authentication
if "auth_user" not in st.session_state:
    st.session_state.auth_user = None  # User dict or None

# Header Banner
st.markdown('<div class="main-header">📡 AI + IoT Smart Lost & Found System</div>', unsafe_allow_html=True)
st.markdown('<div class="tagline">“Find what you lost. Return what you found.” | <b>Smart Campus Platform</b></div>', unsafe_allow_html=True)

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

    # 1. STUDENT AUTHENTICATION FLOW
    if auth_role == "👨‍🎓 Student Portal":
        st.subheader("👨‍🎓 Student Access Gateway")
        student_tab1, student_tab2 = st.tabs(["🔑 Student Sign In", "📝 New Student Sign Up"])

        # STUDENT SIGN IN
        with student_tab1:
            st.info("Log in using your registered College Email or Student Roll Number.")
            col_l1, col_l2 = st.columns([2, 1])
            with col_l1:
                with st.form("student_login_form"):
                    identifier = st.text_input("College Email or Roll Number *", placeholder="e.g. rahul.sharma@campus.edu or 2300970100045")
                    password = st.text_input("Password *", type="password", placeholder="Enter your password")
                    btn_login = st.form_submit_button("🚀 Sign In to Student Portal", use_container_width=True, type="primary")

                    if btn_login:
                        if not identifier or not password:
                            st.error("Please enter both identifier and password.")
                        else:
                            # Match in DB
                            users = db.get_users()
                            matched = None
                            for u in users:
                                if (u.get("email", "").lower() == identifier.strip().lower() or 
                                    (u.get("student_id") and u.get("student_id").lower() == identifier.strip().lower())):
                                    if u.get("role") == "student":
                                        matched = u
                                        break
                            if matched:
                                if matched.get("password") and matched.get("password") != password:
                                    st.error("Incorrect password. Please try again.")
                                else:
                                    st.session_state.auth_user = matched
                                    st.success(f"Welcome back, {matched.get('name')}!")
                                    st.rerun()
                            else:
                                st.error("No student account found with these credentials. Please check or sign up.")

            with col_l2:
                st.markdown("#### ⚡ Quick Demo Student Login")
                st.caption("One-click login with pre-configured student profile:")
                if st.button("👤 Sign In as Rahul Sharma (CSE)", use_container_width=True):
                    demo_user = db.get_user_by_email("rahul.sharma@campus.edu")
                    if not demo_user:
                        demo_user = {
                            "id": "USR-101",
                            "name": "Rahul Sharma",
                            "email": "rahul.sharma@campus.edu",
                            "password": "student123",
                            "role": "student",
                            "student_id": "2300970100045",
                            "department": "Computer Science & Engineering",
                            "semester": "Semester 3",
                            "phone": "+91 9876543210"
                        }
                        db.add_user(User(**demo_user))
                    st.session_state.auth_user = demo_user
                    st.rerun()

        # STUDENT SIGN UP
        with student_tab2:
            st.info("Register your student profile to report lost items, trace dropboxes, and submit return claims.")
            with st.form("student_signup_form"):
                col_s1, col_s2 = st.columns(2)
                with col_s1:
                    s_name = st.text_input("Full Name *", placeholder="e.g. Aryan Khan")
                    s_roll = st.text_input("Student Roll Number / Enrollment ID *", placeholder="e.g. 2300970100120")
                    s_email = st.text_input("College Email Address *", placeholder="e.g. aryan.khan@campus.edu")
                with col_s2:
                    s_dept = st.selectbox("Branch / Department *", [
                        "Computer Science & Engineering",
                        "Information Technology",
                        "Electronics & Communication",
                        "Mechanical Engineering",
                        "Civil Engineering",
                        "Electrical Engineering",
                        "MBA / Management",
                        "Other"
                    ])
                    s_sem = st.selectbox("Current Semester / Year *", [
                        "Semester 1 (1st Year)",
                        "Semester 2 (1st Year)",
                        "Semester 3 (2nd Year)",
                        "Semester 4 (2nd Year)",
                        "Semester 5 (3rd Year)",
                        "Semester 6 (3rd Year)",
                        "Semester 7 (4th Year)",
                        "Semester 8 (4th Year)"
                    ])
                    s_phone = st.text_input("Contact Mobile Number *", placeholder="+91 9876543210")

                s_pass = st.text_input("Create Password *", type="password", placeholder="Minimum 6 characters")
                s_pass_conf = st.text_input("Confirm Password *", type="password", placeholder="Re-enter password")
                
                btn_signup = st.form_submit_button("📝 Complete Student Registration", use_container_width=True, type="primary")

                if btn_signup:
                    if not s_name or not s_roll or not s_email or not s_pass:
                        st.error("Please fill in all mandatory fields (*).")
                    elif s_pass != s_pass_conf:
                        st.error("Passwords do not match!")
                    elif db.get_user_by_email(s_email):
                        st.error("A student account with this email is already registered. Please sign in.")
                    else:
                        new_student = User(
                            id=f"USR-{uuid.uuid4().hex[:6].upper()}",
                            name=s_name,
                            email=s_email,
                            password=s_pass,
                            role="student",
                            student_id=s_roll,
                            department=s_dept,
                            semester=s_sem,
                            phone=s_phone
                        )
                        saved_user = db.add_user(new_student)
                        st.session_state.auth_user = saved_user
                        st.success(f"Registration successful! Welcome to the Smart Lost & Found platform, {s_name}!")
                        st.rerun()

    # 2. ADMINISTRATOR AUTHENTICATION FLOW
    elif auth_role == "🛡️ Administrator Portal":
        st.subheader("🛡️ Campus Administrator & Proctor Login")
        st.warning("Authorized faculty, security officers, and proctorial board members only.")
        
        col_a1, col_a2 = st.columns([2, 1])
        with col_a1:
            with st.form("admin_login_form"):
                admin_email = st.text_input("Administrator Email *", placeholder="e.g. admin@campus.edu")
                admin_password = st.text_input("Admin Master Password *", type="password", placeholder="Enter admin password")
                btn_admin = st.form_submit_button("🛡️ Authenticate as Administrator", use_container_width=True, type="primary")

                if btn_admin:
                    if not admin_email or not admin_password:
                        st.error("Please enter administrator credentials.")
                    elif admin_email.strip().lower() == "admin@campus.edu" and admin_password == "admin123":
                        admin_user = db.get_user_by_email("admin@campus.edu")
                        if not admin_user:
                            admin_user = {
                                "id": "USR-ADMIN",
                                "name": "Prof. S. K. Mehta (Campus Administrator)",
                                "email": "admin@campus.edu",
                                "password": "admin123",
                                "role": "admin",
                                "student_id": "ADMIN-001",
                                "department": "Proctorial Board",
                                "semester": "Staff / Faculty",
                                "phone": "+91 9876543299"
                            }
                            db.add_user(User(**admin_user))
                        st.session_state.auth_user = admin_user
                        st.success("Administrator login authenticated!")
                        st.rerun()
                    else:
                        # Check existing DB admin users
                        user = db.get_user_by_email(admin_email)
                        if user and user.get("role") == "admin" and user.get("password") == admin_password:
                            st.session_state.auth_user = user
                            st.success(f"Welcome, {user.get('name')}!")
                            st.rerun()
                        else:
                            st.error("Invalid administrator credentials. Access Denied.")

        with col_a2:
            st.markdown("#### 🔑 Quick Admin Login")
            st.caption("Default administrative credentials for project demonstration:")
            st.code("Email: admin@campus.edu\nPass:  admin123", language="text")
            if st.button("🛡️ 1-Click Login as Campus Admin", use_container_width=True):
                admin_user = db.get_user_by_email("admin@campus.edu")
                if not admin_user:
                    admin_user = {
                        "id": "USR-ADMIN",
                        "name": "Prof. S. K. Mehta (Campus Administrator)",
                        "email": "admin@campus.edu",
                        "password": "admin123",
                        "role": "admin",
                        "student_id": "ADMIN-001",
                        "department": "Proctorial Board",
                        "semester": "Staff / Faculty",
                        "phone": "+91 9876543299"
                    }
                    db.add_user(User(**admin_user))
                st.session_state.auth_user = admin_user
                st.rerun()

    st.stop()

# -------------------------------------------------------------
# LOGGED-IN APPLICATION SHELL
# -------------------------------------------------------------
current_user = st.session_state.auth_user
is_admin = current_user.get("role") == "admin"

# Sidebar
with st.sidebar:
    st.image("https://images.unsplash.com/photo-1541339907198-e08756dedf3f?w=400", use_container_width=True)
    
    # User Profile Card
    badge_class = "badge-admin" if is_admin else "badge-student"
    role_title = "CAMPUS ADMINISTRATOR" if is_admin else "STUDENT"
    st.markdown(f'<span class="role-badge {badge_class}">🛡️ {role_title}</span>', unsafe_allow_html=True)
    st.markdown(f"**👤 {current_user.get('name')}**")
    st.caption(f"🆔 {current_user.get('student_id')} | 📧 {current_user.get('email')}")
    if not is_admin:
        st.caption(f"🏫 {current_user.get('department', 'CSE')} • {current_user.get('semester', 'Sem 3')}")
    
    if st.button("🚪 Sign Out", use_container_width=True):
        st.session_state.auth_user = None
        st.rerun()

    st.markdown("---")
    st.markdown("### 🧭 Navigation")
    
    if is_admin:
        menu = st.radio(
            "Admin Operations:",
            [
                "📊 Master Analytics & Heatmap",
                "🛡️ Claims Verification Desk",
                "📦 Smart Drop Box Hardware Monitor",
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
                "👤 My Profile & History"
            ]
        )

    st.markdown("---")
    st.caption("AI + IoT Lost & Found • v2.0 • Production")


# =============================================================
# STUDENT PORTAL VIEWS
# =============================================================
if not is_admin:

    # 1. STUDENT DASHBOARD
    if menu == "🏠 Student Dashboard":
        lost_items = db.get_lost_items()
        found_items = db.get_found_items()
        my_lost = [l for l in lost_items if l.user_id == current_user.get("id") or l.user_email == current_user.get("email")]
        my_claims = [c for c in db.get_claims() if c.student_email == current_user.get("email") or c.student_id == current_user.get("student_id")]
        
        # Student KPI banner
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("🚨 My Lost Reports", len(my_lost))
        with col2:
            st.metric("📦 Campus Found Items", len(found_items))
        with col3:
            st.metric("🎯 My Claims Filed", len(my_claims))
        with col4:
            all_matches = db.get_all_matches(min_score=60.0)
            my_matches = [m for m in all_matches if m.lost_item.user_email == current_user.get("email")]
            st.metric("🧠 Active AI Matches", len(my_matches))

        st.markdown("---")

        col_l, col_r = st.columns(2)
        with col_l:
            st.subheader("📋 My Reported Lost Items")
            if not my_lost:
                st.info("You haven't reported any lost items yet. Use the 'Report Lost Item' tab to log one.")
            else:
                for item in my_lost:
                    with st.container(border=True):
                        c1, c2 = st.columns([3, 1])
                        with c1:
                            st.markdown(f"**{item.item_name}** (`{item.category}`)")
                            st.caption(f"📍 Last seen: {item.last_seen_location} • ⏰ {item.lost_time}")
                            st.write(f"*{item.description}*")
                        with c2:
                            badge_color = "green" if item.status == "RETURNED" else ("orange" if item.status == "CLAIMED" else "red")
                            st.markdown(f":{badge_color}[**{item.status}**]")

        with col_r:
            st.subheader("🟢 Recent Found Items on Campus")
            for item in found_items[:4]:
                with st.container(border=True):
                    c1, c2 = st.columns([3, 1])
                    with c1:
                        st.markdown(f"**{item.item_name}** (`{item.category}`)")
                        st.caption(f"📍 Found at: {item.found_location} • 📡 Source: {item.source}")
                        st.write(f"*{item.description}*")
                    with c2:
                        st.markdown(f":blue[**{item.status}**]")

    # 2. REPORT LOST ITEM
    elif menu == "❓ Report Lost Item":
        st.subheader("📝 Report a Lost Item")
        st.info(f"Reporting as **{current_user.get('name')}** (Roll: {current_user.get('student_id')}). Once submitted, our AI engine automatically checks existing Smart Drop Box deposits.")

        with st.form("lost_form"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Item Name *", placeholder="e.g. Boat Wireless Earbuds")
                category = st.selectbox("Category *", ["Electronics", "Accessories", "Documents", "Bags", "Stationery", "Other"])
                brand = st.text_input("Brand / Make", placeholder="e.g. Boat / Wildhorn / Casio")
            with col2:
                color = st.text_input("Primary Color *", placeholder="e.g. White / Black / Silver")
                location = st.selectbox("Last Seen Location *", ["Library", "Canteen", "Main Gate", "Admin Block", "Sports Complex", "Classroom Hall"])
                time_lost = st.text_input("Approximate Time *", placeholder="e.g. 2:30 PM today")
            
            description = st.text_area("Detailed Description *", placeholder="Provide unique features, scratches, case color, markings, or contents inside.")
            submitted = st.form_submit_button("🚀 Submit & Scan AI Database", use_container_width=True, type="primary")

            if submitted:
                if not name or not color or not description:
                    st.error("Please fill all required fields (*).")
                else:
                    new_item = LostItem(
                        id=f"LOST-{uuid.uuid4().hex[:4].upper()}",
                        user_id=current_user.get("id"),
                        user_name=current_user.get("name"),
                        user_email=current_user.get("email"),
                        student_id=current_user.get("student_id"),
                        item_name=name,
                        category=category,
                        brand=brand,
                        color=color,
                        last_seen_location=location,
                        lost_time=time_lost,
                        description=description,
                        status="LOST"
                    )
                    db.add_lost_item(new_item)
                    st.success(f"✅ Lost report registered successfully with ID: **{new_item.id}**!")
                    
                    # Check immediate matches
                    matches = [m for m in db.get_all_matches(min_score=60.0) if m.lost_item.id == new_item.id]
                    if matches:
                        st.balloons()
                        st.markdown(f"### 🎉 Immediate AI Matches Found ({len(matches)} item(s)):")
                        for m in matches:
                            st.success(f"**{m.breakdown.final_score}% Match:** Found '{m.found_item.item_name}' at {m.found_item.found_location} (Source: {m.found_item.source})!")

    # 3. REPORT FOUND ITEM
    elif menu == "🎁 Report Found Item":
        st.subheader("📦 Report a Found Item (Manual Submission)")
        st.write(f"Logged in as **{current_user.get('name')}**. If you picked up an item and want to register it for the owner, submit the details below:")

        with st.form("found_form"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Item Name *", placeholder="e.g. Casio Scientific Calculator")
                category = st.selectbox("Category *", ["Stationery", "Electronics", "Accessories", "Documents", "Bags", "Other"])
                brand = st.text_input("Brand / Make", placeholder="e.g. Casio")
            with col2:
                color = st.text_input("Color *", placeholder="e.g. Black")
                location = st.selectbox("Found Location *", ["Admin Block", "Library", "Canteen", "Main Gate", "Sports Complex"])
                found_time = st.text_input("Found Time", placeholder="e.g. 12:30 PM")

            description = st.text_area("Detailed Description *", placeholder="Describe exact location, condition, markings, etc.")
            submitted = st.form_submit_button("✅ Register Found Item", use_container_width=True, type="primary")

            if submitted:
                if not name or not color or not description:
                    st.error("Please fill all required fields.")
                else:
                    new_fnd = FoundItem(
                        id=f"FND-{uuid.uuid4().hex[:4].upper()}",
                        item_name=name,
                        category=category,
                        brand=brand,
                        color=color,
                        found_location=location,
                        found_time=found_time or "Recently",
                        description=description,
                        source="MANUAL",
                        reported_by_id=current_user.get("id"),
                        reported_by_name=current_user.get("name"),
                        status="FOUND"
                    )
                    db.add_found_item(new_fnd)
                    st.success(f"🎉 Thank you, {current_user.get('name')}! Found item recorded with ID: **{new_fnd.id}**")

    # 4. MY MATCHES & CLAIM DESK
    elif menu == "🎯 My Matches & Claim Desk":
        st.subheader("🎯 AI Match Finder & Item Claim Portal")
        st.caption("AI compares your lost items with physical Smart Drop Box items using 6-Factor Semantic Matching.")

        all_matches = db.get_all_matches(min_score=50.0)
        # Filter for this student or show general matches if none
        my_matches = [m for m in all_matches if m.lost_item.user_email == current_user.get("email") or m.lost_item.student_id == current_user.get("student_id")]
        
        display_matches = my_matches if my_matches else all_matches

        if not display_matches:
            st.info("No matching pairs found in the database. Report a lost item to trigger matching.")
        else:
            if not my_matches:
                st.caption("Showing campus-wide match matrix (Report an item to view personalized matches):")
            for m in display_matches:
                with st.container(border=True):
                    c1, c2, c3 = st.columns([1, 3, 1.2])
                    with c1:
                        score_color = "purple" if m.breakdown.final_score >= 80 else "blue"
                        st.markdown(f"### :{score_color}[{m.breakdown.final_score}%]")
                        st.caption(f"Tier: **{m.breakdown.tier}**")
                    with c2:
                        st.markdown(f"**Lost:** `{m.lost_item.item_name}` ↔ **Found:** `{m.found_item.item_name}`")
                        st.write(f"📍 Location: **{m.lost_item.last_seen_location}** ↔ **{m.found_item.found_location}** | Source: **{m.found_item.source}**")
                        
                        # Score Breakdown
                        sc1, sc2, sc3, sc4, sc5 = st.columns(5)
                        sc1.caption(f"Text: **{m.breakdown.text_score}%**")
                        sc2.caption(f"Cat: **{m.breakdown.category_score}%**")
                        sc3.caption(f"Color: **{m.breakdown.color_score}%**")
                        sc4.caption(f"Loc: **{m.breakdown.location_score}%**")
                        sc5.caption(f"Brand: **{m.breakdown.brand_score}%**")
                    with c3:
                        with st.popover("🙋 File Claim"):
                            st.markdown(f"**Claim Item:** {m.lost_item.item_name}")
                            st.caption("Provide secret proof only the genuine owner would know (e.g. scratch, lock screen, invoice, inside contents):")
                            secret = st.text_area("Proof of Ownership:", placeholder="Detailed proof...", key=f"secret_{m.id}")
                            if st.button("Submit to Proctor", key=f"btn_{m.id}", type="primary"):
                                if secret.strip():
                                    claim = Claim(
                                        id=f"CLM-{uuid.uuid4().hex[:5].upper()}",
                                        lost_item_id=m.lost_item.id,
                                        found_item_id=m.found_item.id,
                                        student_id=current_user.get("student_id", "2300970100045"),
                                        student_name=current_user.get("name", "Student"),
                                        student_email=current_user.get("email", "student@campus.edu"),
                                        item_name=m.lost_item.item_name,
                                        secret_details=secret,
                                        status="PENDING"
                                    )
                                    db.add_claim(claim)
                                    st.success("Claim submitted to Proctor for verification!")
                                else:
                                    st.error("Please enter proof details.")

    # 5. VIRTUAL IOT DROP BOX
    elif menu == "📟 Virtual IoT Drop Box":
        st.subheader("📟 ESP32 Smart Drop Box #BOX-001 (Hardware Simulator)")
        st.caption("Test the physical campus smart drop box: RFID scan, OLED status, and SG90 servo door lock.")

        col_box, col_input = st.columns([3, 2])
        with col_box:
            st.markdown("""
            <div class="oled-box">
                <div style="display:flex; justify-content:space-between; border-bottom:1px solid #155e75; padding-bottom:4px;">
                    <span>CAMPUS SMART DROP BOX</span>
                    <span>ONLINE 📶</span>
                </div>
                <div style="font-size: 1.2rem; font-weight:bold; margin-top:12px; color:#e0f2fe;">
                    STATUS: READY TO SCAN
                </div>
                <div style="font-size: 0.9rem; color:#38bdf8; margin-top:4px;">
                    Tap RFID Tag & Deposit Item
                </div>
                <div style="border-top:1px solid #164e63; margin-top:14px; padding-top:4px; display:flex; justify-content:space-between; font-size:0.75rem; color:#0284c7;">
                    <span>SERVO: LOCKED (0°)</span>
                    <span>BOX-001 (Library)</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("#### 📟 Live ESP32 UART Serial Monitor")
            serial_log = """[BOOT] ESP32-WROOM-32 boot complete.
[NET] Connected to Campus_WiFi (IP: 192.168.1.104)
[RFID] MFRC-522 initialized on SPI pins (18, 19, 23, 5)
[OLED] SSD1306 128x64 display ready on I2C (21, 22)
[SERVO] SG90 calibrated to 0 deg (Door Locked)
[SYSTEM] Listening for found item deposits..."""
            st.code(serial_log, language="bash")

        with col_input:
            st.markdown("#### 📥 Drop Item via RFID")
            box_id = st.selectbox("Drop Box Location:", ["BOX-001 (Library)", "BOX-002 (Canteen)", "BOX-003 (Main Gate)", "BOX-004 (Admin Block)"])
            rfid_tag = st.selectbox("RFID Tag UID:", ["RFID-1024 (Wallet Tag)", "RFID-E204A1 (Earbuds Tag)", "RFID-KEY-88 (Keys Tag)", "RFID-CALC-09 (Calculator Tag)"])
            dep_name = st.text_input("Deposited Item Name:", value="Black Leather Wallet")
            dep_cat = st.selectbox("Category:", ["Accessories", "Electronics", "Documents", "Bags", "Stationery"])
            dep_color = st.text_input("Color:", value="Black")
            dep_brand = st.text_input("Brand:", value="Wildhorn")
            dep_desc = st.text_area("Description:", value="Black leather wallet with college ID inside.")

            if st.button("🏷️ Tap RFID & Deposit into Box", use_container_width=True, type="primary"):
                box_code = box_id.split()[0]
                clean_rfid = rfid_tag.split()[0]
                
                new_fnd = FoundItem(
                    id=f"FND-IOT-{uuid.uuid4().hex[:4].upper()}",
                    item_name=dep_name,
                    category=dep_cat,
                    brand=dep_brand,
                    color=dep_color,
                    found_location="Library" if "BOX-001" in box_code else "Campus",
                    found_time=datetime.datetime.now().strftime("%I:%M %p"),
                    description=dep_desc,
                    source="IOT_BOX",
                    box_id=box_code,
                    rfid_tag=clean_rfid,
                    reported_by_id=current_user.get("id"),
                    reported_by_name=current_user.get("name"),
                    status="FOUND"
                )
                db.add_found_item(new_fnd)
                
                st.success(f"🎉 **ITEM DEPOSITED!** Tag: `{clean_rfid}` logged in `{box_code}`.")
                st.info("SG90 Servo door unlocked for 5 seconds -> Item deposited -> Box locked.")
                
                matches = [m for m in db.get_all_matches(min_score=60.0) if m.found_item.id == new_fnd.id]
                if matches:
                    st.balloons()
                    st.success(f"🧠 **AI Match Alert:** Matched **{matches[0].breakdown.final_score}%** with Lost Item: '{matches[0].lost_item.item_name}'")

    # 6. MY PROFILE & HISTORY
    elif menu == "👤 My Profile & History":
        st.subheader("👤 Student Profile & History")
        
        c_p1, c_p2 = st.columns(2)
        with c_p1:
            with st.container(border=True):
                st.markdown("#### 🎓 Student Information")
                st.write(f"**Full Name:** {current_user.get('name')}")
                st.write(f"**Roll Number / ID:** {current_user.get('student_id')}")
                st.write(f"**College Email:** {current_user.get('email')}")
                st.write(f"**Branch / Dept:** {current_user.get('department', 'Computer Science & Engineering')}")
                st.write(f"**Current Semester:** {current_user.get('semester', 'Semester 3')}")
                st.write(f"**Phone Number:** {current_user.get('phone', 'N/A')}")
        
        with c_p2:
            with st.container(border=True):
                st.markdown("#### 📜 My Submitted Claims")
                my_claims = [c for c in db.get_claims() if c.student_email == current_user.get("email") or c.student_id == current_user.get("student_id")]
                if not my_claims:
                    st.info("No claims submitted yet.")
                else:
                    for c in my_claims:
                        st.markdown(f"**{c.item_name}** — Status: `{c.status}`")
                        st.caption(f"Proof: *\"{c.secret_details}\"*")
                        if c.status == "APPROVED":
                            st.success("🎉 Approved! Collect your item from the Proctor Office.")
                        st.divider()


# =============================================================
# ADMINISTRATOR PORTAL VIEWS
# =============================================================
else:

    # 1. ADMIN ANALYTICS
    if menu == "📊 Master Analytics & Heatmap":
        st.subheader("📊 Campus Master Incident Analytics & Loss Heatmap")
        
        lost_items = db.get_lost_items()
        found_items = db.get_found_items()
        claims = db.get_claims()
        matches = db.get_all_matches(min_score=60.0)
        returned = len([l for l in lost_items if l.status == "RETURNED"])
        recovery_rate = round((returned / len(lost_items) * 100) if lost_items else 0.0, 1)

        # Metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("🚨 Total Lost Reports", len(lost_items))
        with col2:
            st.metric("📦 Found Items Deposited", len(found_items))
        with col3:
            st.metric("🧠 AI Matches Detected", len(matches))
        with col4:
            st.metric("🏆 Recovery Rate", f"{recovery_rate}%")

        st.markdown("---")

        col_chart1, col_chart2 = st.columns(2)
        with col_chart1:
            st.markdown("#### 🥧 Category Distribution")
            cats = [l.category for l in lost_items] + [f.category for f in found_items]
            cat_counts = dict(Counter(cats))
            if not cat_counts:
                cat_counts = {"Electronics": 4, "Accessories": 3, "Stationery": 2}
            fig_pie = px.pie(names=list(cat_counts.keys()), values=list(cat_counts.values()), hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(fig_pie, use_container_width=True)

        with col_chart2:
            st.markdown("#### 📍 Loss Hotspot Locations")
            locs = [l.last_seen_location for l in lost_items] + [f.found_location for f in found_items]
            loc_counts = dict(Counter(locs))
            if not loc_counts:
                loc_counts = {"Library": 5, "Canteen": 3, "Main Gate": 2, "Admin Block": 2}
            fig_bar = px.bar(x=list(loc_counts.keys()), y=list(loc_counts.values()), labels={'x': 'Campus Location', 'y': 'Incidents'}, color=list(loc_counts.values()))
            st.plotly_chart(fig_bar, use_container_width=True)

    # 2. CLAIMS VERIFICATION DESK
    elif menu == "🛡️ Claims Verification Desk":
        st.subheader("🛡️ Proctor & Faculty Verification Desk")
        st.caption("Review ownership secret proofs submitted by students before authorizing item release.")

        claims = db.get_claims()
        if not claims:
            st.info("No claims currently pending review.")
        else:
            for c in claims:
                with st.container(border=True):
                    col_info, col_action = st.columns([3, 1.2])
                    with col_info:
                        st.markdown(f"**Item:** `{c.item_name}` | Status: **{c.status}**")
                        st.write(f"Student: **{c.student_name}** (Roll: `{c.student_id}` • `{c.student_email}`)")
                        st.markdown(f"🔒 **Secret Ownership Proof:** *\"{c.secret_details}\"*")
                    with col_action:
                        if c.status == "PENDING":
                            if st.button("✅ Approve & Release", key=f"app_{c.id}", type="primary"):
                                db.update_claim(c.id, "APPROVED", "Proof verified by Proctor")
                                db.update_lost_item_status(c.lost_item_id, "RETURNED")
                                db.update_found_item_status(c.found_item_id, "RETURNED")
                                st.success("Claim approved and item marked as RETURNED!")
                                st.rerun()
                            if st.button("❌ Reject Claim", key=f"rej_{c.id}"):
                                db.update_claim(c.id, "REJECTED", "Proof insufficient")
                                st.error("Claim rejected.")
                                st.rerun()
                        else:
                            st.markdown(f"Decision: **{c.status}**")

    # 3. SMART DROP BOX HARDWARE MONITOR
    elif menu == "📦 Smart Drop Box Hardware Monitor":
        st.subheader("📦 IoT Smart Drop Box Fleet Management")
        
        boxes = [
            {"id": "BOX-001", "location": "Library 1st Floor", "ip": "192.168.1.104", "status": "ONLINE", "rfid": "Active", "servo": "Locked (0°)", "last_ping": "2s ago"},
            {"id": "BOX-002", "location": "Student Canteen", "ip": "192.168.1.105", "status": "ONLINE", "rfid": "Active", "servo": "Locked (0°)", "last_ping": "4s ago"},
            {"id": "BOX-003", "location": "Main Entrance Gate", "ip": "192.168.1.106", "status": "ONLINE", "rfid": "Active", "servo": "Locked (0°)", "last_ping": "1s ago"},
            {"id": "BOX-004", "location": "Admin Block Foyer", "ip": "192.168.1.107", "status": "ONLINE", "rfid": "Active", "servo": "Locked (0°)", "last_ping": "8s ago"},
        ]
        st.dataframe(boxes, use_container_width=True)

        st.markdown("#### 🕹️ Remote Administrative Actuator Override")
        c_ov1, c_ov2, c_ov3 = st.columns(3)
        with c_ov1:
            target_box = st.selectbox("Target Hardware Box:", ["BOX-001", "BOX-002", "BOX-003", "BOX-004"])
        with c_ov2:
            if st.button("🔓 Remote Unlock Servo Door (90°)", use_container_width=True):
                st.warning(f"Sent HTTP command `POST /api/iot/actuate` -> `{target_box}` Servo unlocked.")
        with c_ov3:
            if st.button("🔒 Force Lock Box Door (0°)", use_container_width=True):
                st.success(f"Sent HTTP command `POST /api/iot/actuate` -> `{target_box}` Servo locked.")

    # 4. GLOBAL AI MATCH MATRIX
    elif menu == "🧠 Global AI Match Matrix":
        st.subheader("🧠 Global AI Multi-Factor Match Matrix")
        st.caption("Cross-matching all lost reports with all physical deposits.")

        tier_filter = st.selectbox("Filter Confidence Tier:", ["All Matches (>=50%)", "High Probability (>=80%)", "Possible Matches (60-79%)"])
        min_s = 80.0 if "High" in tier_filter else (60.0 if "Possible" in tier_filter else 50.0)
        matches = db.get_all_matches(min_score=min_s)

        if not matches:
            st.info("No matching pairs found.")
        else:
            for m in matches:
                with st.container(border=True):
                    c1, c2 = st.columns([1, 4])
                    with c1:
                        score_color = "purple" if m.breakdown.final_score >= 80 else "blue"
                        st.markdown(f"### :{score_color}[{m.breakdown.final_score}%]")
                        st.caption(f"Tier: **{m.breakdown.tier}**")
                    with c2:
                        st.markdown(f"**Lost:** `{m.lost_item.item_name}` (Reported by: {m.lost_item.user_name}) ↔ **Found:** `{m.found_item.item_name}` (Source: {m.found_item.source})")
                        st.write(f"📍 Location: **{m.lost_item.last_seen_location}** ↔ **{m.found_item.found_location}**")
                        sc1, sc2, sc3, sc4, sc5 = st.columns(5)
                        sc1.caption(f"Text: **{m.breakdown.text_score}%**")
                        sc2.caption(f"Cat: **{m.breakdown.category_score}%**")
                        sc3.caption(f"Color: **{m.breakdown.color_score}%**")
                        sc4.caption(f"Loc: **{m.breakdown.location_score}%**")
                        sc5.caption(f"Brand: **{m.breakdown.brand_score}%**")

    # 5. MASTER INVENTORY & LOGS
    elif menu == "📋 Master Inventory & Logs":
        st.subheader("📋 Master Campus Inventory & Audit Logs")
        
        tab_inv1, tab_inv2, tab_inv3 = st.tabs(["📦 Found Items Inventory", "🚨 Lost Items Registry", "👥 Registered Users"])
        
        with tab_inv1:
            found_items = db.get_found_items()
            st.dataframe([{
                "ID": f.id,
                "Name": f.item_name,
                "Category": f.category,
                "Brand": f.brand,
                "Color": f.color,
                "Location": f.found_location,
                "Source": f.source,
                "RFID Tag": f.rfid_tag or "N/A",
                "Status": f.status
            } for f in found_items], use_container_width=True)

        with tab_inv2:
            lost_items = db.get_lost_items()
            st.dataframe([{
                "ID": l.id,
                "Name": l.item_name,
                "Category": l.category,
                "Brand": l.brand,
                "Color": l.color,
                "Last Seen": l.last_seen_location,
                "Reported By": l.user_name,
                "Student ID": l.student_id,
                "Status": l.status
            } for l in lost_items], use_container_width=True)

        with tab_inv3:
            users = db.get_users()
            st.dataframe([{
                "ID": u.get("id"),
                "Name": u.get("name"),
                "Email": u.get("email"),
                "Role": u.get("role"),
                "Student/Staff ID": u.get("student_id"),
                "Department": u.get("department"),
                "Semester": u.get("semester"),
                "Phone": u.get("phone")
            } for u in users], use_container_width=True)
