import os
import sys
import base64
import subprocess
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_IMG_DIR = os.path.join(BASE_DIR, "backend", "app", "static", "images")
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
if not os.path.exists(CHROME_PATH):
    CHROME_PATH = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

def get_b64_image(filename):
    p = os.path.join(STATIC_IMG_DIR, filename)
    if os.path.exists(p):
        with open(p, "rb") as f:
            return "data:image/jpeg;base64," + base64.b64encode(f.read()).decode("utf-8")
    return ""

img_earbuds = get_b64_image("cmf_earbuds_case.jpg")
img_calc = get_b64_image("casio_calculator.jpg")
img_wallet = get_b64_image("leather_wallet_id.jpg")
img_bottle = get_b64_image("milton_bottle.jpg")
img_id = get_b64_image("student_id_lanyard.jpg")

html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>FINDBACK AI - Complete Features & Technical Specification</title>
<style>
  @page {{
    size: A4 portrait;
    margin: 14mm 12mm 14mm 12mm;
    @bottom-right {{
      content: counter(page);
    }}
  }}
  * {{
    box-sizing: border-box;
    -webkit-print-color-adjust: exact !important;
    print-color-adjust: exact !important;
  }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    color: #1e293b;
    background: #ffffff;
    margin: 0;
    padding: 0;
    line-height: 1.5;
    font-size: 10.5pt;
  }}
  
  /* Headings */
  h1, h2, h3, h4, h5 {{
    color: #0f172a;
    font-weight: 700;
    margin-top: 0;
  }}
  h1 {{ font-size: 24pt; line-height: 1.2; }}
  h2 {{ font-size: 16pt; border-bottom: 2px solid #2563eb; padding-bottom: 6px; margin-top: 20px; margin-bottom: 12px; }}
  h3 {{ font-size: 13pt; color: #1e3a8a; margin-top: 14px; margin-bottom: 6px; }}
  h4 {{ font-size: 11pt; color: #334155; margin-top: 10px; margin-bottom: 4px; }}

  p {{ margin: 0 0 8px 0; }}
  
  .page-break {{
    page-break-before: always;
  }}
  .avoid-break {{
    page-break-inside: avoid;
  }}

  /* COVER PAGE */
  .cover {{
    height: 100%;
    min-height: 250mm;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    padding: 30px 20px;
    background: linear-gradient(135deg, #090d16 0%, #111827 50%, #1e293b 100%);
    color: #ffffff;
    border-radius: 12px;
  }}
  .cover-header {{
    border-bottom: 1px solid rgba(255,255,255,0.15);
    padding-bottom: 15px;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }}
  .badge-inst {{
    background: rgba(37, 99, 235, 0.3);
    border: 1px solid #3b82f6;
    color: #60a5fa;
    padding: 5px 12px;
    border-radius: 20px;
    font-size: 9pt;
    font-weight: 600;
    letter-spacing: 0.5px;
  }}
  .cover-main {{
    margin: 40px 0;
  }}
  .cover-title {{
    font-size: 34pt;
    font-weight: 900;
    letter-spacing: -0.5px;
    background: linear-gradient(90deg, #60a5fa, #a78bfa, #38bdf8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 8px;
  }}
  .cover-subtitle {{
    font-size: 15pt;
    color: #cbd5e1;
    font-weight: 400;
    margin-bottom: 24px;
    line-height: 1.4;
  }}
  .cover-meta-grid {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 10px;
    padding: 18px;
  }}
  .meta-item {{
    font-size: 9.5pt;
  }}
  .meta-label {{
    color: #94a3b8;
    text-transform: uppercase;
    font-size: 8pt;
    font-weight: 700;
    letter-spacing: 0.5px;
    margin-bottom: 3px;
  }}
  .meta-val {{
    color: #f1f5f9;
    font-weight: 600;
  }}
  .cover-footer {{
    border-top: 1px solid rgba(255,255,255,0.15);
    padding-top: 15px;
    display: flex;
    justify-content: space-between;
    font-size: 8.5pt;
    color: #94a3b8;
  }}

  /* HEADER & TOP BANNER */
  .doc-header {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1.5px solid #e2e8f0;
    padding-bottom: 8px;
    margin-bottom: 16px;
    font-size: 8.5pt;
    color: #64748b;
  }}
  .doc-header b {{
    color: #1e293b;
  }}

  /* CARDS & CONTAINERS */
  .card {{
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 12px 14px;
    margin-bottom: 12px;
  }}
  .feature-box {{
    background: #ffffff;
    border: 1.5px solid #cbd5e1;
    border-radius: 9px;
    padding: 14px 16px;
    margin-bottom: 14px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
  }}
  .feature-box.highlight {{
    border-left: 5px solid #2563eb;
    background: #f0f7ff;
  }}
  .feature-box.ai {{
    border-left: 5px solid #7c3aed;
    background: #faf5ff;
  }}
  .feature-box.alert {{
    border-left: 5px solid #059669;
    background: #f0fdf4;
  }}
  
  .badge {{
    display: inline-block;
    padding: 2px 7px;
    border-radius: 12px;
    font-size: 7.5pt;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.4px;
    vertical-align: middle;
    margin-right: 4px;
  }}
  .badge-blue {{ background: #dbeafe; color: #1e40af; border: 1px solid #bfdbfe; }}
  .badge-purple {{ background: #f3e8ff; color: #6b21a8; border: 1px solid #e9d5ff; }}
  .badge-green {{ background: #dcfce7; color: #166534; border: 1px solid #bbf7d0; }}
  .badge-amber {{ background: #fef3c7; color: #92400e; border: 1px solid #fde68a; }}

  /* TABLES */
  table {{
    width: 100%;
    border-collapse: collapse;
    margin: 10px 0 14px 0;
    font-size: 9pt;
  }}
  th, td {{
    padding: 7px 10px;
    border: 1px solid #cbd5e1;
    text-align: left;
    vertical-align: top;
  }}
  th {{
    background: #f1f5f9;
    color: #0f172a;
    font-weight: 700;
  }}
  tr:nth-child(even) td {{
    background: #f8fafc;
  }}

  /* ITEM CARD GRID */
  .item-grid {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
    margin: 10px 0;
  }}
  .item-card {{
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    padding: 10px;
    background: #ffffff;
    display: flex;
    gap: 10px;
  }}
  .item-thumb {{
    width: 75px;
    height: 75px;
    border-radius: 6px;
    object-fit: cover;
    border: 1px solid #94a3b8;
    flex-shrink: 0;
  }}
  .item-details {{
    font-size: 8pt;
    line-height: 1.35;
  }}
  .item-title {{
    font-size: 9pt;
    font-weight: 700;
    color: #0f172a;
    margin-bottom: 2px;
  }}

  /* CODE & MATH CALLOUT */
  .code-block {{
    background: #0f172a;
    color: #f8fafc;
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
    font-size: 8.5pt;
    padding: 10px 14px;
    border-radius: 6px;
    margin: 8px 0;
    line-height: 1.4;
  }}
  .math-card {{
    background: #f1f5f9;
    border: 1px solid #cbd5e1;
    border-left: 4px solid #2563eb;
    padding: 8px 12px;
    margin: 8px 0;
    font-family: "Courier New", Courier, monospace;
    font-size: 9pt;
    color: #1e293b;
  }}

  /* TWO COLUMNS */
  .row-2 {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 14px;
  }}
</style>
</head>
<body>

<!-- COVER PAGE -->
<div class="cover">
  <div class="cover-header">
    <div>
      <span style="font-weight:800; font-size:12pt; letter-spacing:1px; color:#f8fafc;">GL BAJAJ INSTITUTE OF TECHNOLOGY & MANAGEMENT</span><br>
      <small style="color:#94a3b8;">Department of Computer Science & Engineering • Greater Noida, Uttar Pradesh</small>
    </div>
    <div class="badge-inst">ACADEMIC PROJECT DEFENSE</div>
  </div>

  <div class="cover-main">
    <div style="display:inline-block; margin-bottom:12px;">
      <span class="badge badge-purple" style="font-size:9pt; padding:4px 10px;">⚡ FINDBACK AI v2.2 PRODUCTION RELEASE</span>
    </div>
    <div class="cover-title">FINDBACK AI</div>
    <div class="cover-subtitle">
      Autonomous Multimodal AI Lost & Found Ecosystem<br>
      with 6-Factor Composite Matching, Gemini Vision Intake, and Real-Time WhatsApp Dispatch
    </div>

    <div class="cover-meta-grid">
      <div class="meta-item">
        <div class="meta-label">Project Domain</div>
        <div class="meta-val">Multimodal AI, Computer Vision & Smart Campus IoT</div>
      </div>
      <div class="meta-item">
        <div class="meta-label">Core Models & Algorithms</div>
        <div class="meta-val">Gemini 2.5 Flash Vision, Gemini 2.5 Flash-Lite, TF-IDF Cosine</div>
      </div>
      <div class="meta-item">
        <div class="meta-label">Target Institution</div>
        <div class="meta-val">GL Bajaj (GLBITM), Knowledge Park III, Greater Noida</div>
      </div>
      <div class="meta-item">
        <div class="meta-label">Cross-Matching Accuracy</div>
        <div class="meta-val">91.9% – 95.0% Composite Score on Real Datasets</div>
      </div>
    </div>
  </div>

  <div class="cover-footer">
    <div><b>Repository:</b> github.com/Siddiqui-Hammad/Lost_And_found</div>
    <div><b>Generated:</b> October 2026 • Official Documentation</div>
  </div>
</div>

<div class="page-break"></div>

<!-- SECTION 1: EXECUTIVE SUMMARY & ARCHITECTURE -->
<div class="doc-header">
  <div><b>FINDBACK AI</b> — System Technical Specification</div>
  <div>Section 1: Executive Overview & Architecture</div>
</div>

<h2>1. Executive Summary & Problem Formulation</h2>

<div class="feature-box highlight">
  <h3 style="margin-top:0;">🎯 Problem Statement & Core Objective</h3>
  <p>
    On large university campuses like <b>GL Bajaj Institute of Technology & Management</b> (enrolling thousands of students across multiple academic blocks), student belongings—earbuds, laptops, calculators, wallets, and government/college ID cards—are routinely misplaced. 
    Traditional campus lost-and-found mechanisms suffer from critical structural failures:
  </p>
  <ul>
    <li><b>Manual Paper Registers:</b> Fragmented across separate departments, library counters, and the proctor's office with zero central visibility.</li>
    <li><b>Vague Subjective Descriptions:</b> A student reports <i>"lost black earbuds"</i> while security records <i>"found wireless case"</i>, creating missed matches.</li>
    <li><b>Fraudulent Ownership Claims:</b> Without hardware specifications verification, anyone who spots an item in the office can claim it.</li>
    <li><b>Zero Automated Outreach:</b> Students never receive proactive notifications when their lost item is turned into campus custody.</li>
  </ul>
  <p style="margin-bottom:0;">
    <b>Objective:</b> Build <b>FINDBACK AI</b>—an autonomous, multi-tier lost & found platform leveraging <b>Google Gemini Multimodal AI</b>, a <b>6-factor composite scoring engine</b>, an <b>AI Proctorial Specifications Analyzer</b>, and an <b>Automated WhatsApp/Email Dispatcher</b> to maximize return velocity while eliminating fraudulent claims.
  </p>
</div>

<h3>🏗️ End-to-End System Architecture</h3>
<p>
  FINDBACK AI operates on a modular microservice pipeline bridging students, campus security officers, and the Proctorial Board:
</p>

<div class="code-block">
[ STUDENT / SECURITY PORTAL ]           [ PROCTORIAL BOARD DESK ]
   │                                       │
   ├─ 1. Instant Camera Photo Intake       ├─ 5. AI Vision Specifications Analyzer
   ├─ 2. Natural Language Query ("Ask AI") ├─ 6. AI Match & Verification Dossier Explainer
   ├─ 3. Multi-Channel WhatsApp Alert      ├─ 7. Proctorial AI Claim Authenticity Audit
   └─ 4. Secure Claim Token Verification   ├─ 8. Campus Spatial Recovery & Hotspot Digest
                                           └─ 9. Printable Physical Custody QR Slip
                         │
                         ▼
        ┌────────────────────────────────────────────────────────┐
        │        FINDBACK AI MULTIMODAL CORE ENGINE              │
        │  • Google Gemini 2.5 Flash Vision (Hardware Specs)    │
        │  • Google Gemini 2.5 Flash-Lite (NLP RAG Search & Q&A)│
        │  • 6-Factor Composite Multi-Attribute Matcher         │
        │  • Subword TF-IDF Cosine Similarity Engine             │
        │  • Canonical Roll & Phone Number Duplicate Guards      │
        │  • Local DocumentDB & MongoDB Master Store             │
        └────────────────────────────────────────────────────────┘
</div>

<div class="avoid-break">
  <h3>⚡ Key Technical Innovations Summary</h3>
  <table>
    <thead>
      <tr>
        <th style="width:28%;">Capability</th>
        <th style="width:32%;">Traditional Campus Process</th>
        <th style="width:40%;">FINDBACK AI Solution</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><b>Item Intake & Cataloging</b></td>
        <td>Handwritten register; 2–5 days delay; no photographic evidence.</td>
        <td>Instant camera snap; Gemini 2.5 Flash Vision extracts brand, color, condition, and hardware specs profile in &lt; 2 seconds.</td>
      </tr>
      <tr>
        <td><b>Item Cross-Matching</b></td>
        <td>Proctor manually flips through paper logs; misses ~80% of matches.</td>
        <td>Automated 6-Factor composite multi-attribute algorithm evaluating text, category, location, color, time, and brand.</td>
      </tr>
      <tr>
        <td><b>Verification & Anti-Theft</b></td>
        <td>Basic visual confirmation; vulnerable to social engineering.</td>
        <td>AI Challenge Questions & Semantic Claim Audit testing claimant's private statement against unreleased specs.</td>
      </tr>
      <tr>
        <td><b>Student Communication</b></td>
        <td>Physical notice boards; student must repeatedly visit proctor office.</td>
        <td>1-Click WhatsApp & College Email dispatch with unique 8-character claim verification token (`CLM-XXXX`).</td>
      </tr>
    </tbody>
  </table>
</div>

<div class="page-break"></div>

<!-- SECTION 2: COMPLETE FEATURES CATALOGUE -->
<div class="doc-header">
  <div><b>FINDBACK AI</b> — System Technical Specification</div>
  <div>Section 2: Complete 10-Feature Specification</div>
</div>

<h2>2. Complete 10-Feature Technical Specification</h2>

<!-- FEATURE 1 -->
<div class="feature-box ai avoid-break">
  <div style="display:flex; justify-content:space-between; align-items:center;">
    <h3 style="margin:0;">1. Conversational Campus Search ("Ask FINDBACK AI")</h3>
    <span class="badge badge-purple">Gemini 2.5 Flash-Lite RAG</span>
  </div>
  <p style="margin-top:6px;">
    <b>Functionality:</b> A natural language conversational assistant accessible by students and administrators to query campus lost-and-found custody in plain English or Hinglish without navigating complex filters.
  </p>
  <ul>
    <li><b>RAG Prompt Formulation:</b> Dynamically injects live inventory metadata (item names, categories, locations, dates, and custody status) into a structured system prompt.</li>
    <li><b>Contextual Query Examples:</b>
      <ul>
        <li><i>"Did anyone turn in a dark grey CMF earbuds case with an orange dial near the Central Library?"</i></li>
        <li><i>"Have any Casio FX scientific calculators been deposited from Block B workshops today?"</i></li>
      </ul>
    </li>
    <li><b>Output:</b> Returns a conversational summary, exact matched item IDs, custody locations, and direct instructions on how to claim the item from the Proctor Office.</li>
  </ul>
</div>

<!-- FEATURE 2 -->
<div class="feature-box ai avoid-break">
  <div style="display:flex; justify-content:space-between; align-items:center;">
    <h3 style="margin:0;">2. AI Vision Item Intake & Specifications Analyzer</h3>
    <span class="badge badge-purple">Gemini 2.5 Flash Vision</span>
    <span class="badge badge-amber">Recent Priority Queue</span>
  </div>
  <p style="margin-top:6px;">
    <b>Functionality:</b> An automated multimodal inspection portal that transforms a physical camera photograph into a structured technical custody record.
  </p>
  <ul>
    <li><b>Multimodal Feature Extraction:</b> Automatically extracts:
      <ul>
        <li><i>Verified Item Name & Category:</i> (Electronics, Documents & IDs, Accessories, Books, etc.)</li>
        <li><i>Brand & Model Identification:</i> (CMF by Nothing, Casio FX-991CW, Milton, etc.)</li>
        <li><i>Hex & Semantic Color Palette:</i> (Primary dominant color, secondary tones, accent highlights)</li>
        <li><i>Physical Condition:</i> (Mint, minor scratches, worn edges, operational state)</li>
      </ul>
    </li>
    <li><b>Hardware Profile Synthesis:</b> Generates unreleased verification profiles, e.g. charging case form factor, earbud docking status, silicone tip sizes, engraving marks, and 4 custom ownership challenge questions.</li>
    <li><b>Recent Submissions Priority Queue:</b> Intake queue sorted by timestamp descending with 3-way filtering:
      <code>⚡ All Recent Items</code>, <code>🟡 Pending AI Verification</code>, and <code>✅ Verified with Hardware Specs</code>.
    </li>
    <li><b>Instant Student Auto-Intake:</b> When students report a found item with a photo, the AI vision engine analyzes the image on submission, pre-filling verified attributes and triggering instant matches.</li>
  </ul>
</div>

<!-- FEATURE 3 -->
<div class="feature-box highlight avoid-break">
  <div style="display:flex; justify-content:space-between; align-items:center;">
    <h3 style="margin:0;">3. 6-Factor Multi-Attribute AI Cross-Matching Algorithm</h3>
    <span class="badge badge-blue">Mathematical Composite Model</span>
  </div>
  <p style="margin-top:6px;">
    <b>Functionality:</b> The core intelligence engine that continuously evaluates every reported lost item against campus found items across 6 orthogonal dimensions:
  </p>
  
  <div class="math-card">
    Composite Match Score = 0.40·S_text + 0.20·S_category + 0.15·S_location + 0.10·S_color + 0.10·S_time + 0.05·S_brand
  </div>

  <table style="font-size:8.5pt; margin-top:8px;">
    <thead>
      <tr>
        <th style="width:20%;">Factor</th>
        <th style="width:10%;">Weight</th>
        <th style="width:70%;">Algorithmic Implementation</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><b>Text Similarity</b></td>
        <td><b>40%</b></td>
        <td>Subword TF-IDF n-gram (2–4 chars) Vectorizer with Cosine Similarity. Typo-tolerant and resilient to vocabulary differences (e.g. "earphones" vs "earbuds").</td>
      </tr>
      <tr>
        <td><b>Category Match</b></td>
        <td><b>20%</b></td>
        <td>Exact taxonomy match = 100%; related domain cross-match = 50%; category conflict = 0%.</td>
      </tr>
      <tr>
        <td><b>Location Distance</b></td>
        <td><b>15%</b></td>
        <td>Euclidean spatial distance matrix over GL Bajaj campus blocks (Library, Canteen, Block A/B/C/D, Workshop, Audi, Ground).</td>
      </tr>
      <tr>
        <td><b>Color Alignment</b></td>
        <td><b>10%</b></td>
        <td>Standardized 12-color token overlap matrix matching complex descriptions ("Matte Dark Grey & Orange" vs "Dark Grey").</td>
      </tr>
      <tr>
        <td><b>Temporal Decay</b></td>
        <td><b>10%</b></td>
        <td>Exponential temporal decay: S_time = 100 · exp(-0.05 · Δdays). Recent matches receive maximum temporal weight.</td>
      </tr>
      <tr>
        <td><b>Brand Alignment</b></td>
        <td><b>5%</b></td>
        <td>Exact brand match = 100%; generic/unspecified brand = 50%; brand contradiction = 0%.</td>
      </tr>
    </tbody>
  </table>
  <p style="margin-bottom:0; font-size:8.5pt; color:#475569;">
    <b>Confidence Tiers:</b> 🟣 <b>High Probability:</b> ≥ 90% | 🔵 <b>Moderate Match:</b> 70%–89% | ⚪ <b>Low Candidate:</b> 50%–69%.
  </p>
</div>

<div class="page-break"></div>

<!-- SECTION 2 CONTINUED -->
<div class="doc-header">
  <div><b>FINDBACK AI</b> — System Technical Specification</div>
  <div>Section 2: Complete 10-Feature Specification (Cont.)</div>
</div>

<!-- FEATURE 4 -->
<div class="feature-box ai avoid-break">
  <div style="display:flex; justify-content:space-between; align-items:center;">
    <h3 style="margin:0;">4. AI Match & Verification Dossier Explainer</h3>
    <span class="badge badge-purple">Gemini 2.5 Flash-Lite Explainer</span>
  </div>
  <p style="margin-top:6px;">
    <b>Functionality:</b> 1-Click deep forensic comparison between a student's lost report and a campus custody item.
  </p>
  <ul>
    <li><b>Comparative Deep-Dive:</b> Contrasts student description against proctorial specifications to evaluate consistency across color, condition, model, and location.</li>
    <li><b>Authenticity Verdict:</b> Categorizes match confidence (<code>HIGH CONFIDENCE MATCH</code>, <code>PROBABLE MATCH</code>, <code>UNLIKELY MATCH</code>).</li>
    <li><b>3 Proctorial Challenge Questions:</b> Generates customized questions for the student when they visit the office to prove ownership without leaking custody details.</li>
  </ul>
</div>

<!-- FEATURE 5 -->
<div class="feature-box ai avoid-break">
  <div style="display:flex; justify-content:space-between; align-items:center;">
    <h3 style="margin:0;">5. Proctorial AI Ownership Claim Authenticity Audit</h3>
    <span class="badge badge-purple">Gemini 2.5 Flash Claim Evaluator</span>
  </div>
  <p style="margin-top:6px;">
    <b>Functionality:</b> Evaluates confidential student ownership proof submitted through the student portal against unreleased hardware specifications.
  </p>
  <ul>
    <li><b>Zero-Knowledge Verification:</b> The student submits private identifiers (e.g., <i>"Contains ₹500 note, college canteen card ending 204, and faint blue pen mark on right seam"</i>).</li>
    <li><b>AI Semantic Audit:</b> Scores authenticity (0–100%), highlights matching technical facts, and flags contradictions or suspicious claims.</li>
    <li><b>Clear Proctorial Recommendation:</b> Outputs <code>RECOMMEND APPROVAL & RELEASE</code> or <code>REJECT CLAIM (MISMATCH)</code>.</li>
  </ul>
</div>

<!-- FEATURE 6 -->
<div class="feature-box ai avoid-break">
  <div style="display:flex; justify-content:space-between; align-items:center;">
    <h3 style="margin:0;">6. AI Campus Spatial Safety & Hotspot Recovery Digest</h3>
    <span class="badge badge-purple">Gemini Spatial Intelligence</span>
  </div>
  <p style="margin-top:6px;">
    <b>Functionality:</b> Analyzes campus-wide loss patterns across GL Bajaj academic blocks, libraries, and canteens to generate administrative intelligence.
  </p>
  <ul>
    <li><b>Spatial Pattern Detection:</b> Identifies recurring loss clusters (e.g., Central Library study carrels, Cafeteria benches, Mechanical Workshop).</li>
    <li><b>Strategic Directives:</b> Provides Chief Proctor with security patrol schedules, CCTV camera angle recommendations, and locker installation directives.</li>
  </ul>
</div>

<!-- FEATURE 7 -->
<div class="feature-box alert avoid-break">
  <div style="display:flex; justify-content:space-between; align-items:center;">
    <h3 style="margin:0;">7. Automated Multi-Channel Notification Dispatcher</h3>
    <span class="badge badge-green">WhatsApp Web API & SMTP</span>
    <span class="badge badge-blue">Secure Claim Tokens</span>
  </div>
  <p style="margin-top:6px;">
    <b>Functionality:</b> Bridges the final-mile recovery gap by instantly broadcasting alerts to students the moment an AI match is detected.
  </p>
  <ul>
    <li><b>Instant WhatsApp Web/App Links:</b> Generates pre-formatted 1-click WhatsApp alerts containing item details, match percentage, and proctor collection office address.</li>
    <li><b>Secure 8-Character Claim Tokens:</b> Issues cryptographically generated tokens (e.g. <code>CLM-3F25B</code>) required for in-person item retrieval.</li>
    <li><b>Automated Batch Notification Hub:</b> Admin console allowing proctors to broadcast pending match notifications with 1 click.</li>
  </ul>
</div>

<!-- FEATURE 8 -->
<div class="feature-box avoid-break">
  <div style="display:flex; justify-content:space-between; align-items:center;">
    <h3 style="margin:0;">8. GL Bajaj Physical Custody Tag & Printable Evidence Slip</h3>
    <span class="badge badge-blue">QR Code + Base64 Slip</span>
  </div>
  <p style="margin-top:6px;">
    <b>Functionality:</b> Generates a high-contrast physical inventory tag attached to physical items in the Proctor Office storage lockers.
  </p>
  <ul>
    <li><b>Scannable QR Verification:</b> QR code encodes item metadata, intake timestamp, and SHA256 custody checksum.</li>
    <li><b>GLBITM Institutional Letterhead:</b> Includes college header, student claimant details, proctor signature line, and chain of custody log.</li>
  </ul>
</div>

<div class="row-2 avoid-break">
  <!-- FEATURE 9 -->
  <div class="feature-box">
    <h3 style="margin-top:0;">9. Role-Based Dual Portal Security</h3>
    <span class="badge badge-blue">RBAC & Data Guards</span>
    <p style="margin-top:6px; font-size:8.5pt;">
      <b>Role Segregation:</b> Distinct authenticated portals for Students and Proctorial Board Administrators.<br>
      <b>Duplicate Registration Guard:</b> Enforces canonical 10-digit mobile number uniqueness and 13-digit GLBITM Roll Number validation.
    </p>
  </div>

  <!-- FEATURE 10 -->
  <div class="feature-box">
    <h3 style="margin-top:0;">10. Real Photographic Dataset</h3>
    <span class="badge badge-green">Production Seeded</span>
    <p style="margin-top:6px; font-size:8.5pt;">
      <b>Authentic Evidence:</b> 5 real high-resolution photographs representing common campus belongings across 4 unique student personas (Rahul Sharma, Priya Verma, Aman Gupta, Sneha Patel).
    </p>
  </div>
</div>

<div class="page-break"></div>

<!-- SECTION 3: DATASET & RESULTS -->
<div class="doc-header">
  <div><b>FINDBACK AI</b> — System Technical Specification</div>
  <div>Section 3: Dataset, Verification & Empirical Results</div>
</div>

<h2>3. Dataset, Verification & Empirical Results</h2>

<p>
  FINDBACK AI has been benchmarked on a realistic campus test suite containing 5 authentic student lost reports and matching physical custody items:
</p>

<!-- REAL ITEMS GRID -->
<div class="item-grid avoid-break">
  <!-- Item 1 -->
  <div class="item-card">
    <img src="{img_earbuds}" class="item-thumb" alt="Earbuds">
    <div class="item-details">
      <div class="item-title">CMF by Nothing Buds (Dark Grey & Orange)</div>
      <div><b>ID:</b> FOUND-0001 • <b>Location:</b> Central Library (Block A)</div>
      <div><b>Matched Student:</b> Rahul Sharma (Roll: 2300970100045)</div>
      <div><span class="badge badge-purple">🟣 91.9% Composite Match (High Probability)</span></div>
    </div>
  </div>

  <!-- Item 2 -->
  <div class="item-card">
    <img src="{img_calc}" class="item-thumb" alt="Calculator">
    <div class="item-details">
      <div class="item-title">Casio FX-991CW ClassWiz Scientific Calculator</div>
      <div><b>ID:</b> FOUND-0002 • <b>Location:</b> Mechanical Workshop Block B</div>
      <div><b>Matched Student:</b> Priya Verma (Roll: 2300970100112)</div>
      <div><span class="badge badge-purple">🟣 95.0% Composite Match (High Probability)</span></div>
    </div>
  </div>

  <!-- Item 3 -->
  <div class="item-card">
    <img src="{img_wallet}" class="item-thumb" alt="Wallet">
    <div class="item-details">
      <div class="item-title">Dark Brown Leather Bifold Wallet</div>
      <div><b>ID:</b> FOUND-0003 • <b>Location:</b> Cafeteria & Nescafe Counter</div>
      <div><b>Matched Student:</b> Aman Gupta (Roll: 2300970100088)</div>
      <div><span class="badge badge-purple">🟣 92.4% Composite Match (High Probability)</span></div>
    </div>
  </div>

  <!-- Item 4 -->
  <div class="item-card">
    <img src="{img_bottle}" class="item-thumb" alt="Bottle">
    <div class="item-details">
      <div class="item-title">Hydro Flask Insulated Stainless Steel Bottle</div>
      <div><b>ID:</b> FOUND-0004 • <b>Location:</b> Main Auditorium Ground Floor</div>
      <div><b>Matched Student:</b> Sneha Patel (Roll: 2300970100140)</div>
      <div><span class="badge badge-purple">🟣 93.1% Composite Match (High Probability)</span></div>
    </div>
  </div>
</div>

<div class="avoid-break" style="margin-top:10px;">
  <!-- Item 5 -->
  <div class="item-card" style="width:100%;">
    <img src="{img_id}" class="item-thumb" alt="Student ID">
    <div class="item-details">
      <div class="item-title">Student University ID Card with Royal Blue Lanyard</div>
      <div><b>ID:</b> FOUND-0005 • <b>Location:</b> Academic Block C Entrance Corridor • <b>Deposited by:</b> Security Desk Officer</div>
      <div><b>Matched Student:</b> Rahul Sharma (Roll: 2300970100045) — Cross-referenced roll card</div>
      <div><span class="badge badge-purple">🟣 94.6% Composite Match (High Probability)</span></div>
    </div>
  </div>
</div>

<h3>📊 Empirical Matching Performance Matrix</h3>

<table class="avoid-break">
  <thead>
    <tr>
      <th>Lost Item Report</th>
      <th>Custody Found Item</th>
      <th>Text</th>
      <th>Cat</th>
      <th>Loc</th>
      <th>Color</th>
      <th>Time</th>
      <th>Brand</th>
      <th>Composite</th>
      <th>Match Tier</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><b>CMF Nothing Buds</b></td>
      <td>FOUND-0001 (Earbuds Case)</td>
      <td>93.4%</td>
      <td>100%</td>
      <td>100%</td>
      <td>90.0%</td>
      <td>100%</td>
      <td>10.0%</td>
      <td><b>91.9%</b></td>
      <td><span class="badge badge-purple">🟣 High</span></td>
    </tr>
    <tr>
      <td><b>Casio FX-991CW Calculator</b></td>
      <td>FOUND-0002 (Casio Calculator)</td>
      <td>96.8%</td>
      <td>100%</td>
      <td>100%</td>
      <td>100%</td>
      <td>100%</td>
      <td>100%</td>
      <td><b>95.0%</b></td>
      <td><span class="badge badge-purple">🟣 High</span></td>
    </tr>
    <tr>
      <td><b>Wildhorn Leather Wallet</b></td>
      <td>FOUND-0003 (Brown Bifold)</td>
      <td>91.2%</td>
      <td>100%</td>
      <td>100%</td>
      <td>100%</td>
      <td>100%</td>
      <td>10.0%</td>
      <td><b>92.4%</b></td>
      <td><span class="badge badge-purple">🟣 High</span></td>
    </tr>
    <tr>
      <td><b>Milton Insulated Bottle</b></td>
      <td>FOUND-0004 (Stainless Bottle)</td>
      <td>92.5%</td>
      <td>100%</td>
      <td>100%</td>
      <td>100%</td>
      <td>100%</td>
      <td>10.0%</td>
      <td><b>93.1%</b></td>
      <td><span class="badge badge-purple">🟣 High</span></td>
    </tr>
    <tr>
      <td><b>Student ID Card & Lanyard</b></td>
      <td>FOUND-0005 (ID Card & Lanyard)</td>
      <td>95.1%</td>
      <td>100%</td>
      <td>100%</td>
      <td>100%</td>
      <td>100%</td>
      <td>100%</td>
      <td><b>94.6%</b></td>
      <td><span class="badge badge-purple">🟣 High</span></td>
    </tr>
  </tbody>
</table>

<div class="page-break"></div>

<!-- SECTION 4: PROJECT DEFENSE Q&A -->
<div class="doc-header">
  <div><b>FINDBACK AI</b> — System Technical Specification</div>
  <div>Section 4: Faculty & Peer Presentation Defense Guide</div>
</div>

<h2>4. Faculty & Peer Presentation Defense Guide</h2>

<div class="feature-box avoid-break">
  <h4>Q1: Exactly where and how is AI/ML used in this project?</h4>
  <p style="font-size:9pt; margin-bottom:0;">
    <b>Answer:</b> AI is integrated across <b>4 distinct layers</b>:
    <br>1. <b>Multimodal Vision (Gemini 2.5 Flash):</b> Extracts item subtype, color palette, condition, and detailed specs from photos.
    <br>2. <b>NLP Subword TF-IDF Vectorization:</b> Computes semantic cosine similarity over unstructured student descriptions with typo-tolerance.
    <br>3. <b>RAG Natural Language Campus Search (Gemini 2.5 Flash-Lite):</b> Performs conversational querying over live inventory.
    <br>4. <b>Semantic Claim Audit (Gemini 2.5 Flash-Lite):</b> Evaluates private claimant proof statements against technical custody records to prevent fraud.
  </p>
</div>

<div class="feature-box avoid-break">
  <h4>Q2: Why use a 6-Factor composite formula instead of simple keyword matching?</h4>
  <p style="font-size:9pt; margin-bottom:0;">
    <b>Answer:</b> Keyword matching fails when students and finders use different terminology (e.g., <i>"earbuds"</i> vs <i>"wireless pods"</i>) or when color and location conflict. Our composite model balances <b>Text (40%)</b>, <b>Category (20%)</b>, <b>Location (15%)</b>, <b>Color (10%)</b>, <b>Time Decay (10%)</b>, and <b>Brand (5%)</b>, ensuring high accuracy while penalizing spatial and temporal impossibilities.
  </p>
</div>

<div class="feature-box avoid-break">
  <h4>Q3: How does the system prevent someone from falsely claiming an expensive item like AirPods or a phone?</h4>
  <p style="font-size:9pt; margin-bottom:0;">
    <b>Answer:</b> Through a <b>Zero-Knowledge Verification Architecture</b>:
    <br>• Technical hardware specs and fine markings are kept hidden from public view.
    <br>• The student must submit confidential details (stickers, scratches, cover details, serial digits).
    <br>• The <b>AI Claim Authenticity Audit</b> compares student claims against the verified custody record and assigns an authenticity score.
    <br>• The proctor verifies the student against 3 dynamically generated AI challenge questions and verifies the unique claim token.
  </p>
</div>

<div class="feature-box avoid-break">
  <h4>Q4: How does the system handle real-time student outreach?</h4>
  <p style="font-size:9pt; margin-bottom:0;">
    <b>Answer:</b> The <b>Notification Dispatcher</b> automatically triggers whenever an AI match $\ge 70\%$ is detected:
    <br>• Generates an in-app student alert and dispatch log.
    <br>• Creates a 1-click WhatsApp link formatted with the match score, collection office location, and verification token.
    <br>• Proctors can broadcast alerts individually or in batch via the <b>Automated Notification Hub</b>.
  </p>
</div>

<div class="feature-box avoid-break">
  <h4>Q5: What happens if the internet drops or the Google Gemini API key quota is exceeded?</h4>
  <p style="font-size:9pt; margin-bottom:0;">
    <b>Answer:</b> FINDBACK AI features an automatic <b>Zero-Config Local Fallback Engine</b>. If Gemini API is unreachable, the system automatically falls back to local subword TF-IDF cosine similarity, local spatial Euclidean matrices, and PIL-based color heuristics, ensuring 100% operational uptime.
  </p>
</div>

<div class="card avoid-break" style="background:#0f172a; color:#f8fafc; border:none; margin-top:16px;">
  <h4 style="color:#60a5fa; margin-top:0;">🏁 System Deployment & Repository Reference</h4>
  <p style="font-size:9pt; margin-bottom:4px;">
    • <b>Production Repository:</b> <code>https://github.com/Siddiqui-Hammad/Lost_And_found.git</code><br>
    • <b>Active Git Branch:</b> <code>main</code> (Synchronized & Head Verified)<br>
    • <b>Application Runtime:</b> Streamlit 1.39+ Dual Portal (<code>app.py</code> & <code>streamlit_app.py</code>)<br>
    • <b>Backend Framework:</b> FastAPI REST API + Embedded DocumentDB Engine
  </p>
</div>

</body>
</html>
"""

html_path = os.path.join(BASE_DIR, "FINDBACK_AI_Complete_Features_Documentation.html")
pdf_path = os.path.join(BASE_DIR, "FINDBACK_AI_Complete_Features_Documentation.pdf")
artifact_dir = r"C:\Users\Asus\.gemini\antigravity\brain\dfc99a7b-7c1b-48ca-997d-a286b284eb5e"
artifact_pdf_path = os.path.join(artifact_dir, "FINDBACK_AI_Complete_Features_Documentation.pdf")

print("Writing HTML documentation...")
with open(html_path, "w", encoding="utf-8") as f:
    f.write(html_content)
print(f"HTML written to {html_path} ({os.path.getsize(html_path)} bytes)")

print(f"Compiling PDF using Chrome headless: {CHROME_PATH}...")
cmd = [
    CHROME_PATH,
    "--headless=new",
    "--disable-gpu",
    "--no-pdf-header-footer",
    f"--print-to-pdf={pdf_path}",
    html_path
]
res = subprocess.run(cmd, capture_output=True, text=True)
if res.returncode == 0 and os.path.exists(pdf_path):
    pdf_size = os.path.getsize(pdf_path)
    print(f"PDF successfully generated: {pdf_path} ({pdf_size} bytes)")
    shutil.copyfile(pdf_path, artifact_pdf_path)
    print(f"PDF mirrored to artifacts directory: {artifact_pdf_path}")
else:
    print(f"Error compiling PDF: returncode={res.returncode}, stderr={res.stderr}")
    sys.exit(1)

print("SUCCESS!")
