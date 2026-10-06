import streamlit as st
import datetime
import uuid
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter

from backend.app.database import db
from backend.app.models import LostItem, FoundItem, Claim, IoTDepositRequest
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
</style>
""", unsafe_allow_html=True)

# App Header
st.markdown('<div class="main-header">📡 AI + IoT Smart Lost & Found System</div>', unsafe_allow_html=True)
st.markdown('<div class="tagline">“Find what you lost. Return what you found.” | <b>AKTU Sem 3 Mini Project</b></div>', unsafe_allow_html=True)

# Sidebar Navigation
with st.sidebar:
    st.image("https://images.unsplash.com/photo-1541339907198-e08756dedf3f?w=400", use_container_width=True)
    st.markdown("### 🧭 Navigation")
    menu = st.radio(
        "Select Portal:",
        [
            "🏠 Campus Dashboard",
            "❓ Report Lost Item",
            "🎁 Report Found Item",
            "🧠 AI Match Matrix",
            "📟 Virtual IoT Smart Box",
            "🛡️ Admin Verification Panel",
            "📊 Campus Analytics & Heatmap",
            "🎓 AKTU Viva & PPT Guide"
        ]
    )
    st.markdown("---")
    st.markdown("**User Profile:** 👤 Rahul Sharma (Student)")
    st.markdown("**Campus Region:** AKTU Main Campus")
    st.caption("v1.0.0 • Production Ready")

# -------------------------------------------------------------
# 1. CAMPUS DASHBOARD
# -------------------------------------------------------------
if menu == "🏠 Campus Dashboard":
    lost_items = db.get_lost_items()
    found_items = db.get_found_items()
    claims = db.get_claims()
    matches = db.get_all_matches(min_score=60.0)
    returned = len([l for l in lost_items if l.status == "RETURNED"])
    recovery_rate = round((returned / len(lost_items) * 100) if lost_items else 0.0, 1)

    # Top KPI Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🚨 Total Lost Reports", len(lost_items), delta="Active Reports")
    with col2:
        st.metric("📦 Found Items Deposited", len(found_items), delta="IoT + Manual")
    with col3:
        st.metric("🧠 AI Matches Detected", len(matches), delta=">=60% Confidence")
    with col4:
        st.metric("🏆 Recovery Rate", f"{recovery_rate}%", delta="Verified & Returned")

    st.markdown("---")
    
    col_left, col_right = st.columns(2)
    with col_left:
        st.subheader("🔴 Recent Lost Items")
        for item in lost_items[:5]:
            with st.container(border=True):
                c1, c2 = st.columns([3, 1])
                with c1:
                    st.markdown(f"**{item.item_name}** (`{item.category}`)")
                    st.caption(f"📍 {item.last_seen_location} • ⏰ {item.lost_time}")
                    st.write(f"*{item.description}*")
                with c2:
                    badge_color = "green" if item.status == "RETURNED" else "red"
                    st.markdown(f":{badge_color}[**{item.status}**]")

    with col_right:
        st.subheader("🟢 Recently Found & Deposited")
        for item in found_items[:5]:
            with st.container(border=True):
                c1, c2 = st.columns([3, 1])
                with c1:
                    st.markdown(f"**{item.item_name}** (`{item.category}`)")
                    st.caption(f"📍 {item.found_location} • 📡 Source: {item.source}")
                    st.write(f"*{item.description}*")
                with c2:
                    st.markdown(f":blue[**{item.status}**]")

# -------------------------------------------------------------
# 2. REPORT LOST ITEM
# -------------------------------------------------------------
elif menu == "❓ Report Lost Item":
    st.subheader("📝 Report a Lost Item")
    st.info("Our AI Semantic Matching Engine will scan all physical IoT dropboxes and found records immediately after submission.")

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
        submitted = st.form_submit_button("🚀 Submit & Trigger AI Match Engine", use_container_width=True)

        if submitted:
            if not name or not color or not description:
                st.error("Please fill all required fields (*).")
            else:
                new_item = LostItem(
                    id=f"LOST-{uuid.uuid4().hex[:4].upper()}",
                    user_id="USR-101",
                    user_name="Rahul Sharma",
                    user_email="rahul.sharma@aktu.ac.in",
                    student_id="2300970100045",
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
                        st.success(f"**{m.breakdown.final_score}% Match:** Found '{m.found_item.item_name}' at {m.found_item.found_location}!")

# -------------------------------------------------------------
# 3. REPORT FOUND ITEM
# -------------------------------------------------------------
elif menu == "🎁 Report Found Item":
    st.subheader("📦 Report a Found Item (Manual Submission)")
    st.write("If you found an item outside the smart dropbox, register it manually here.")

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
        submitted = st.form_submit_button("✅ Register Found Item", use_container_width=True)

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
                    reported_by_name="Good Samaritan",
                    status="FOUND"
                )
                db.add_found_item(new_fnd)
                st.success(f"🎉 Thank you! Found item recorded with ID: **{new_fnd.id}**")

# -------------------------------------------------------------
# 4. AI MATCH MATRIX
# -------------------------------------------------------------
elif menu == "🧠 AI Match Matrix":
    st.subheader("🧠 AI Semantic Matching Matrix")
    st.caption("Weighted scoring: 35% Text Semantics + 20% Category + 15% Color + 10% Brand + 10% Location + 10% Temporal Window")

    tier_filter = st.selectbox("Filter Confidence Tier:", ["All Matches (>=50%)", "High Probability (>=80%)", "Possible Matches (60-79%)"])
    min_s = 80.0 if "High" in tier_filter else (60.0 if "Possible" in tier_filter else 50.0)
    
    matches = db.get_all_matches(min_score=min_s)

    if not matches:
        st.info("No matching pairs found under the selected confidence tier.")
    else:
        for m in matches:
            with st.container(border=True):
                c1, c2, c3 = st.columns([1, 3, 1])
                with c1:
                    score_color = "purple" if m.breakdown.final_score >= 80 else "blue"
                    st.markdown(f"### :{score_color}[{m.breakdown.final_score}%]")
                    st.caption(f"Tier: **{m.breakdown.tier}**")
                with c2:
                    st.markdown(f"**Lost:** `{m.lost_item.item_name}` ↔ **Found:** `{m.found_item.item_name}`")
                    st.write(f"📍 Location: **{m.lost_item.last_seen_location}** ↔ **{m.found_item.found_location}** | Category: **{m.lost_item.category}**")
                    
                    # Score Breakdown metrics
                    sc1, sc2, sc3, sc4, sc5 = st.columns(5)
                    sc1.caption(f"Text: **{m.breakdown.text_score}%**")
                    sc2.caption(f"Cat: **{m.breakdown.category_score}%**")
                    sc3.caption(f"Color: **{m.breakdown.color_score}%**")
                    sc4.caption(f"Loc: **{m.breakdown.location_score}%**")
                    sc5.caption(f"Brand: **{m.breakdown.brand_score}%**")
                with c3:
                    with st.popover("🙋 Claim Item"):
                        st.markdown(f"**Claim Item:** {m.lost_item.item_name}")
                        secret = st.text_area("Proof of Ownership (Secret Details):", placeholder="What was inside? Any scratches, lock PIN, or unique stickers?", key=f"secret_{m.id}")
                        if st.button("Submit Claim to Proctor", key=f"btn_{m.id}"):
                            if secret.strip():
                                claim = Claim(
                                    id=f"CLM-{uuid.uuid4().hex[:5].upper()}",
                                    lost_item_id=m.lost_item.id,
                                    found_item_id=m.found_item.id,
                                    student_id=m.lost_item.student_id or "2300970100045",
                                    student_name=m.lost_item.user_name,
                                    student_email=m.lost_item.user_email,
                                    item_name=m.lost_item.item_name,
                                    secret_details=secret,
                                    status="PENDING"
                                )
                                db.add_claim(claim)
                                st.success("Claim submitted to Proctor successfully!")
                            else:
                                st.error("Please enter proof details.")

# -------------------------------------------------------------
# 5. VIRTUAL IOT SMART BOX SIMULATOR
# -------------------------------------------------------------
elif menu == "📟 Virtual IoT Smart Box":
    st.subheader("📟 ESP32 Smart Drop Box #BOX-001 (Hardware Simulator)")
    st.caption("Simulate physical item deposits with RFID scanning, OLED status feedback, and SG90 servo door control.")

    col_box, col_input = st.columns([3, 2])
    with col_box:
        st.markdown("""
        <div class="oled-box">
            <div style="display:flex; justify-content:space-between; border-bottom:1px solid #155e75; padding-bottom:4px;">
                <span>AKTU SMART LOST BOX</span>
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
        
        st.markdown("#### 📟 Live ESP32 UART Serial Log (115200 Baud)")
        serial_log = """[BOOT] ESP32-WROOM-32 boot complete.
[NET] Connected to Campus_WiFi (IP: 192.168.1.104)
[RFID] MFRC-522 initialized on SPI pins (18, 19, 23, 5)
[OLED] SSD1306 128x64 display ready on I2C (21, 22)
[SERVO] SG90 calibrated to 0 deg (Door Locked)
[SYSTEM] Listening for found item deposits..."""
        st.code(serial_log, language="bash")

    with col_input:
        st.markdown("#### 📥 Deposit Item via RFID")
        box_id = st.selectbox("Select Drop Box Location:", ["BOX-001 (Library)", "BOX-002 (Canteen)", "BOX-003 (Main Gate)", "BOX-004 (Admin Block)"])
        rfid_tag = st.selectbox("RFID Tag UID:", ["RFID-1024 (Wallet Tag)", "RFID-E204A1 (Earbuds Tag)", "RFID-KEY-88 (Keys Tag)", "RFID-CALC-09 (Calculator Tag)"])
        dep_name = st.text_input("Deposited Item Name:", value="Black Leather Wallet")
        dep_cat = st.selectbox("Category:", ["Accessories", "Electronics", "Documents", "Bags", "Stationery"])
        dep_color = st.text_input("Color:", value="Black")
        dep_brand = st.text_input("Brand:", value="Wildhorn")
        dep_desc = st.text_area("Description:", value="Black leather wallet with college ID inside.")

        if st.button("🏷️ Tap RFID & Deposit into Box", use_container_width=True, type="primary"):
            box_code = box_id.split()[0]
            clean_rfid = rfid_tag.split()[0]
            
            # Save deposit
            req = IoTDepositRequest(
                box_id=box_code,
                rfid_tag=clean_rfid,
                item_name=dep_name,
                category=dep_cat,
                brand=dep_brand,
                color=dep_color,
                description=dep_desc
            )
            
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
                reported_by_name=f"{box_code} Smart Box",
                status="FOUND"
            )
            db.add_found_item(new_fnd)
            
            st.success(f"🎉 **ITEM REGISTERED!** Tag: `{clean_rfid}` saved into `{box_code}`.")
            st.info("Servo Door unlocked for 5s -> Item placed -> Auto-locked door.")
            
            matches = [m for m in db.get_all_matches(min_score=60.0) if m.found_item.id == new_fnd.id]
            if matches:
                st.balloons()
                st.success(f"🧠 **AI Match Alert:** Matched **{matches[0].breakdown.final_score}%** with Lost Item: '{matches[0].lost_item.item_name}'")

# -------------------------------------------------------------
# 6. ADMIN VERIFICATION PANEL
# -------------------------------------------------------------
elif menu == "🛡️ Admin Verification Panel":
    st.subheader("🛡️ Proctor & Faculty Verification Portal")
    st.caption("Verify student ownership proof questions and release recovered items.")

    claims = db.get_claims()
    if not claims:
        st.info("No claims currently pending verification.")
    else:
        st.markdown("### 📋 Pending Claims for Proctor Review")
        for c in claims:
            with st.container(border=True):
                col_info, col_action = st.columns([3, 1])
                with col_info:
                    st.markdown(f"**Item:** `{c.item_name}` | Status: **{c.status}**")
                    st.write(f"Claimant: **{c.student_name}** ({c.student_email})")
                    st.markdown(f"🔒 **Secret Proof Provided:** *\"{c.secret_details}\"*")
                with col_action:
                    if c.status == "PENDING":
                        if st.button("✅ Approve & Return", key=f"app_{c.id}"):
                            db.update_claim(c.id, "APPROVED", "Proof verified by Proctor")
                            db.update_lost_item_status(c.lost_item_id, "RETURNED")
                            db.update_found_item_status(c.found_item_id, "RETURNED")
                            st.success("Claim approved and item marked as RETURNED!")
                            st.rerun()
                        if st.button("❌ Reject Claim", key=f"rej_{c.id}"):
                            db.update_claim(c.id, "REJECTED", "Proof mismatch")
                            st.error("Claim rejected.")
                            st.rerun()
                    else:
                        st.markdown(f"Status: **{c.status}**")

    st.markdown("---")
    st.markdown("### 📦 Campus Smart Box & Found Inventory")
    found_items = db.get_found_items()
    table_data = [{
        "Item ID": f.id,
        "Name": f.item_name,
        "Category": f.category,
        "Source": f.source,
        "RFID Tag": f.rfid_tag or "N/A",
        "Location": f.found_location,
        "Status": f.status
    } for f in found_items]
    st.dataframe(table_data, use_container_width=True)

# -------------------------------------------------------------
# 7. CAMPUS ANALYTICS & HEATMAP
# -------------------------------------------------------------
elif menu == "📊 Campus Analytics & Heatmap":
    st.subheader("📊 Campus Lost & Found Analytics")
    
    lost_items = db.get_lost_items()
    found_items = db.get_found_items()
    
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.markdown("#### 🥧 Most Lost Categories")
        cats = [l.category for l in lost_items] + [f.category for f in found_items]
        cat_counts = dict(Counter(cats))
        if not cat_counts:
            cat_counts = {"Electronics": 4, "Accessories": 3, "Stationery": 2}
        fig_pie = px.pie(names=list(cat_counts.keys()), values=list(cat_counts.values()), hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_chart2:
        st.markdown("#### 📍 Campus Loss Hotspots")
        locs = [l.last_seen_location for l in lost_items] + [f.found_location for f in found_items]
        loc_counts = dict(Counter(locs))
        if not loc_counts:
            loc_counts = {"Library": 5, "Canteen": 3, "Main Gate": 2, "Admin Block": 2}
        fig_bar = px.bar(x=list(loc_counts.keys()), y=list(loc_counts.values()), labels={'x': 'Campus Location', 'y': 'Incidents'}, color=list(loc_counts.values()))
        st.plotly_chart(fig_bar, use_container_width=True)

# -------------------------------------------------------------
# 8. AKTU VIVA & PRESENTATION GUIDE
# -------------------------------------------------------------
elif menu == "🎓 AKTU Viva & PPT Guide":
    st.subheader("🎓 AKTU Semester 3 Mini Project Viva & Defense Guide")
    
    st.markdown("""
    ### 🗣️ Top Questions & Examiner Answers:
    
    1. **Where is IoT in this project?**
       - *Answer:* The physical **ESP32 Smart Drop Box** uses an **MFRC-522 RFID reader** to scan items, an **SG90 Servo** for physical lock control, a **0.96" OLED display** for status feedback, and communicates over **Wi-Fi** using HTTP REST endpoints to our backend.
    
    2. **Where is AI in this project?**
       - *Answer:* The **Semantic Matching Engine** uses **TF-IDF token embeddings + Cosine Similarity** for textual descriptions and applies a **6-Factor weighted formula**: 35% Text + 20% Category + 15% Color + 10% Brand + 10% Location + 10% Temporal Window.
    
    3. **Why not return items automatically when AI match is 95%?**
       - *Answer:* To prevent fraudulent claims. The student must submit private ownership proof (e.g. inner contents, unique stickers, wallpaper), and the **Proctor verifies** the proof before marking the item as `RETURNED`.
    
    4. **What is the hardware prototype cost?**
       - *Answer:* Total budget is only **₹850 – ₹1,200 INR** (ESP32: ₹380, RFID: ₹120, OLED: ₹140, Servo+Buzzer: ₹80), making it affordable for campus-wide deployment.
    """)
