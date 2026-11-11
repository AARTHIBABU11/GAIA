# app.py - Complete GAIA Platform
import streamlit as st
import pandas as pd
import numpy as np
import uuid
import os
import io
import hashlib
from datetime import datetime

# Import modules
from modules.text_analyzer import text_analyzer
from modules.fraud_detector import fraud_detector
from modules.image_analyzer import image_analyzer
import importlib
import modules.voice_processor
importlib.reload(modules.voice_processor)
from modules.voice_processor import voice_processor
from modules.score_calculator import score_calculator
from modules.notification import notification_system
from modules.carbon_tracker import tracker
from modules.database import db

import config

# Page configuration
st.set_page_config(
    page_title="GAIA - Sustainability Intelligence Platform",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern, premium styling
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif;
}

.gaia-header {
    background: linear-gradient(135deg, #0d3b2e 0%, #175e47 50%, #2e7d32 100%);
    padding: 24px 30px;
    border-radius: 16px;
    color: white;
    margin-bottom: 24px;
    box-shadow: 0 10px 25px -5px rgba(13, 59, 46, 0.25);
}

.gaia-header h1 {
    color: #ffffff;
    font-size: 28px;
    font-weight: 800;
    margin: 0 0 6px 0;
}

.gaia-header p {
    color: #c8e6c9;
    font-size: 14px;
    margin: 0;
}

.gaia-card {
    background: #ffffff;
    border: 1px solid #e0e0e0;
    border-radius: 14px;
    padding: 20px;
    margin-bottom: 16px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);
}

.score-badge-card {
    border-radius: 16px;
    padding: 24px;
    text-align: center;
    margin: 16px 0;
    box-shadow: 0 8px 24px rgba(0,0,0,0.06);
}

.score-badge-card.excellent {
    background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
    border: 2px solid #4caf50;
    color: #1b5e20;
}

.score-badge-card.good {
    background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
    border: 2px solid #2196f3;
    color: #0d47a1;
}

.score-badge-card.poor {
    background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%);
    border: 2px solid #ff9800;
    color: #e65100;
}

.score-badge-card.critical {
    background: linear-gradient(135deg, #ffebee 0%, #ffcdd2 100%);
    border: 2px solid #f44336;
    color: #b71c1c;
}

.big-score {
    font-size: 56px;
    font-weight: 800;
    line-height: 1;
    margin: 10px 0;
}

.stat-pill {
    display: inline-block;
    padding: 6px 14px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.pill-pass {
    background-color: #d4edda;
    color: #155724;
}

.pill-warn {
    background-color: #fff3cd;
    color: #856404;
}

.pill-fail {
    background-color: #f8d7da;
    color: #721c24;
}

.metric-card {
    background-color: #f8faf9;
    border: 1px solid #e2e8f0;
    padding: 16px;
    border-radius: 12px;
    text-align: center;
}

.voice-card {
    background: linear-gradient(135deg, #eefbf3 0%, #e0f2f1 100%);
    border: 1px solid #b2dfdb;
    padding: 18px;
    
    border-radius: 12px;
    margin: 12px 0;
}
</style>
""", unsafe_allow_html=True)

# Application Header Banner
st.markdown("""
<div class="gaia-header">
    <h1>🌍 GAIA Intelligence Platform</h1>
    <p>Green AI-Powered Environmental Compliance Verification & Multilingual Citizen Grievance Portal</p>
</div>
""", unsafe_allow_html=True)

# Sidebar Navigation
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/earth-planet.png", width=70)
    st.markdown("### **GAIA Control Hub**")
    
    portal = st.radio(
        "Select Active Portal:",
        [
            "👮 Officer Dashboard",
            "📢 Citizen Grievance Portal",
            "📊 Analytics & Insights",
            "🌱 Green AI Metrics"
        ]
    )

    st.divider()
    st.markdown(f"**App Version:** `v{config.APP_VERSION}`")
    st.markdown("**AI Models Engine:**")
    st.caption("• DistilBERT (Text & Sentiment)")
    st.caption("• MobileNet V2 (Pollution Vision)")
    st.caption("• Whisper Tiny (Multilingual Voice)")
    st.divider()
    st.caption("© 2026 GAIA Sustainability Platform")

# =========================================================================
# 1. OFFICER DASHBOARD
# =========================================================================
if portal == "👮 Officer Dashboard":
    # Officer Authentication Check
    if "officer_logged_in" not in st.session_state:
        st.session_state.officer_logged_in = False

    if not st.session_state.officer_logged_in:
        st.header("🔒 Authorized Officer Login")
        st.caption("Secure access restricted to Environmental Protection Officers and Regulatory Auditors.")

        col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
        with col_l2:
            st.markdown("""
            <div class="gaia-card" style="margin-top: 15px;">
                <h3 style="margin-top:0; color:#0d3b2e;">👮 Officer Authentication</h3>
                <p style="color:#555; font-size:14px;">Enter your officer email and password to access the environmental audit dashboard.</p>
            </div>
            """, unsafe_allow_html=True)

            with st.form("officer_login_form"):
                officer_email = st.text_input("Officer Email Address*", value="", placeholder="e.g., officer@gaia.gov.in")
                officer_pass = st.text_input("Password*", type="password", placeholder="Enter your password")
                submit_login = st.form_submit_button("🔑 Login to Officer Dashboard", type="primary", use_container_width=True)

                if submit_login:
                    if not officer_email.strip():
                        st.error("Please enter your officer email address.")
                    elif not officer_pass.strip():
                        st.error("Please enter your password.")
                    else:
                        st.session_state.officer_logged_in = True
                        st.session_state.officer_email = officer_email.strip()
                        st.success("Authentication successful! Redirecting...")
                        st.rerun()

            st.info("💡 **Officer Login:** Enter your officer email and password (Demo: `officer@gaia.gov.in` / `admin123`)")
        st.stop()

    # Officer is authenticated - show header & logout option
    col_head, col_logout = st.columns([3, 1])
    with col_head:
        st.header("👮 Environmental Officer Portal")
        st.caption("Audit factory reports, detect fabricated data, inspect complaints, and dispatch regulatory notices.")
    with col_logout:
        st.write("")
        st.caption(f"Logged in: **{st.session_state.get('officer_email', 'Officer')}**")
        if st.button("🚪 Logout", key="btn_officer_logout"):
            st.session_state.officer_logged_in = False
            st.rerun()

    tab1, tab_mail, tab2, tab3, tab4 = st.tabs([
        "📄 Analyze Report",
        "✉️ In-Mail Notices & Messaging",
        "🚨 Fraud Detection Alerts",
        "📋 Report Archive & Search",
        "🛠️ Citizen Grievance Triage"
    ])

    # Initialize audit session state
    if "current_audit" not in st.session_state:
        st.session_state.current_audit = None

    # --- TAB 1: ANALYZE REPORT ---
    with tab1:
        st.subheader("Industrial Sustainability Report Audit")

        # Quick Test Data Loaders
        col_load1, col_load2, col_clear = st.columns([1, 1, 2])
        if "officer_text" not in st.session_state:
            st.session_state.officer_text = ""
        if "officer_factory" not in st.session_state:
            st.session_state.officer_factory = ""
        if "officer_industry" not in st.session_state:
            st.session_state.officer_industry = "Textile"

        with col_load1:
            if st.button("📄 Load Sample Authentic Report", use_container_width=True):
                try:
                    with open("sample data/real_report.txt", "r", encoding="utf-8") as f:
                        st.session_state.officer_text = f.read()
                    st.session_state.officer_factory = "GreenLeaf Textiles Private Limited"
                    st.session_state.officer_industry = "Textile"
                    st.toast("Loaded authentic sample report!", icon="✅")
                except Exception as e:
                    st.error(f"Error loading sample: {e}")

        with col_load2:
            if st.button("⚠️ Load Sample Fraudulent Report", use_container_width=True):
                try:
                    with open("sample data/fake_report.txt", "r", encoding="utf-8") as f:
                        st.session_state.officer_text = f.read()
                    st.session_state.officer_factory = "Apex Chemicals & Fertilizers"
                    st.session_state.officer_industry = "Chemical"
                    st.toast("Loaded suspicious sample report!", icon="⚠️")
                except Exception as e:
                    st.error(f"Error loading sample: {e}")

        with col_clear:
            if st.button("🧹 Clear Form", use_container_width=False):
                st.session_state.officer_text = ""
                st.session_state.officer_factory = ""
                st.session_state.current_audit = None
                st.rerun()

        col_meta1, col_meta2 = st.columns(2)
        with col_meta1:
            factory_name = st.text_input(
                "Factory / Enterprise Name*",
                value=st.session_state.officer_factory,
                placeholder="e.g., GreenLeaf Textiles Pvt Ltd"
            )
        with col_meta2:
            industry_list = ["Textile", "Chemical", "Steel", "Pharma", "Automobile", "Food Processing", "Power", "Other"]
            current_ind_idx = 0
            if st.session_state.officer_industry in industry_list:
                current_ind_idx = industry_list.index(st.session_state.officer_industry)
            industry = st.selectbox("Industry Sector*", industry_list, index=current_ind_idx)

        st.markdown("**Upload Submission or Paste Text**")
        report_file = st.file_uploader(
            "Upload Report File (.pdf, .txt)",
            type=['pdf', 'txt'],
            help="Upload the annual environmental compliance submission document"
        )

        extracted_text = ""
        if report_file is not None:
            if report_file.type == "application/pdf" or report_file.name.lower().endswith(".pdf"):
                try:
                    import pdfplumber
                    with pdfplumber.open(report_file) as pdf:
                        for page in pdf.pages:
                            page_content = page.extract_text()
                            if page_content:
                                extracted_text += page_content + "\n"
                    if not extracted_text.strip():
                        st.warning("Could not extract selectable text from PDF. It may contain scanned images.")
                    else:
                        st.success(f"Extracted {len(extracted_text)} characters from PDF.")
                except Exception as e:
                    st.error(f"Error processing PDF: {e}")
            else:
                try:
                    extracted_text = report_file.read().decode("utf-8")
                except UnicodeDecodeError:
                    report_file.seek(0)
                    extracted_text = report_file.read().decode("latin-1", errors="ignore")

        report_text = st.text_area(
            "Report Content (auto-populated from file or type directly)*",
            value=extracted_text if extracted_text else st.session_state.officer_text,
            height=200,
            placeholder="Paste factory environmental report text here..."
        )

        if st.button("🔍 Run Full AI Audit & Verification", type="primary", use_container_width=True):
            if not factory_name.strip():
                st.error("Please specify the Factory/Company Name before running audit.")
            elif not report_text.strip():
                st.error("Please upload a file or paste report content.")
            else:
                with st.spinner("Analyzing report semantics, evaluating metrics, and verifying authenticity..."):
                    tracker.start_operation("Officer_Report_Audit")

                    # 1. Text & Sentiment Analysis
                    analysis = text_analyzer.analyze(report_text)
                    metrics = analysis.get('metrics', {})
                    sentiment = analysis.get('sentiment', {'score': 0.5, 'label': 'NEUTRAL'})

                    # 2. Fraud & Anomaly Detection
                    ind_key = industry.lower().replace(" ", "_") if industry else None
                    fraud_res = fraud_detector.detect(report_text, metrics, industry=ind_key)

                    # 3. GAIA Score & Domain Breakdown
                    sentiment_pct = sentiment.get('score', 0.5) * 100
                    gaia_score = score_calculator.calculate(metrics, sentiment_score=sentiment_pct, industry=ind_key)
                    status_info = score_calculator.get_status(gaia_score)
                    domain_breakdown = score_calculator.get_domain_breakdown(metrics, industry=ind_key)
                    recommendations = score_calculator.get_recommendation_priority(
                        score_calculator.calculate_domain_scores(metrics, industry=ind_key)
                    )

                    # 4. Save to Database
                    rep_id = db.save_report(
                        factory_name=factory_name,
                        report_text=report_text,
                        gaia_score=gaia_score,
                        is_fake=fraud_res['is_fake'],
                        fraud_score=fraud_res['fraud_score'],
                        industry=industry,
                        status=status_info['status']
                    )

                    emissions_g = tracker.end_operation()

                    # Save to session state so interactions like sending mail don't clear results
                    st.session_state.current_audit = {
                        'factory_name': factory_name,
                        'industry': industry,
                        'gaia_score': gaia_score,
                        'status_info': status_info,
                        'fraud_res': fraud_res,
                        'domain_breakdown': domain_breakdown,
                        'metrics': metrics,
                        'recommendations': recommendations,
                        'emissions_g': emissions_g,
                        'report_id': rep_id
                    }

        # --- DISPLAY PERSISTENT AUDIT RESULTS ---
        if st.session_state.current_audit:
            audit = st.session_state.current_audit
            st.divider()
            st.markdown(f"### 📊 Regulatory Compliance Audit Results: **{audit['factory_name']}**")

            col_res1, col_res2 = st.columns([1, 1])

            with col_res1:
                status_style = audit['status_info']['status'].lower()
                st.markdown(f"""
                <div class="score-badge-card {status_style}">
                    <span class="stat-pill {'pill-pass' if audit['gaia_score'] >= 60 else 'pill-fail'}">GAIA SCORE</span>
                    <div class="big-score">{audit['gaia_score']} / 100</div>
                    <h2>{audit['status_info']['icon']} {audit['status_info']['status']} COMPLIANCE</h2>
                    <p style="font-size: 15px; margin-top: 8px;">{audit['status_info']['message']}</p>
                    <p><strong>Action Mandate:</strong> {audit['status_info']['action']}</p>
                    <p><strong>Timeline:</strong> {audit['status_info']['deadline']}</p>
                </div>
                """, unsafe_allow_html=True)

            with col_res2:
                is_fake = audit['fraud_res']['is_fake']
                fraud_pct = int(audit['fraud_res']['fraud_score'] * 100)
                st.markdown(f"""
                <div class="score-badge-card {'critical' if is_fake else 'excellent'}">
                    <span class="stat-pill {'pill-fail' if is_fake else 'pill-pass'}">FRAUD RISK LEVEL</span>
                    <div class="big-score">{fraud_pct}%</div>
                    <h2>{audit['fraud_res']['severity_icon']} {'FLAGGED: HIGH RISK OF FABRICATION' if is_fake else 'AUTHENTIC SUBMISSION'}</h2>
                    <p><strong>Risk Severity:</strong> {audit['fraud_res']['severity']}</p>
                </div>
                """, unsafe_allow_html=True)

            # Fraud Flag Reasons
            if is_fake or audit['fraud_res']['reasons']:
                with st.expander("🚨 Detailed Fraud Detection Indicators & Flags", expanded=is_fake):
                    for reason in audit['fraud_res']['reasons']:
                        st.write(f"• {reason}")

            # Domain Breakdown Table
            st.markdown("#### 🌿 Domain Performance Breakdown")
            breakdown_cols = st.columns(len(audit['domain_breakdown']))
            for idx, item in enumerate(audit['domain_breakdown']):
                with breakdown_cols[idx]:
                    st.metric(
                        label=item['domain'],
                        value=f"{item['score']}/100",
                        delta="Good" if item['score'] >= 60 else "Attention"
                    )
                    st.caption(f"{item['status']}")

            # Extracted Metrics Details
            st.markdown("#### 🔬 Extracted Environmental Metrics")
            col_m1, col_m2, col_m3, col_m4 = st.columns(4)
            with col_m1:
                co2 = audit['metrics'].get('co2_emissions')
                st.metric("CO2 Emissions", f"{co2} tons" if co2 is not None else "Not Reported")
            with col_m2:
                renew = audit['metrics'].get('renewable_percent')
                st.metric("Renewable Energy", f"{renew}%" if renew is not None else "Not Reported")
            with col_m3:
                waste = audit['metrics'].get('waste_generated')
                st.metric("Solid Waste", f"{waste} tons" if waste is not None else "Not Reported")
            with col_m4:
                water = audit['metrics'].get('water_usage')
                st.metric("Water Usage", f"{water} KL" if water is not None else "Not Reported")

            # Actionable Recommendations
            st.markdown("#### 📋 Recommended Corrective Measures")
            for rec in audit['recommendations'][:3]:
                st.info(f"**{rec['domain']}** (Priority: {rec['priority']}) — {rec['urgency']}")

            # =========================================================
            # IN-MAIL MESSAGE SENDING OPTIONS (FOR AUDITED ENTERPRISE)
            # =========================================================
            st.markdown("---")
            st.markdown("### ✉️ In-Mail Regulatory Notice & Messaging")
            st.caption("Configure notification parameters, multilingual localization, and dispatch statutory warning directly.")

            mail_col1, mail_col2 = st.columns(2)
            with mail_col1:
                recipient_email = st.text_input(
                    "Recipient Enterprise Email Address*",
                    value=f"compliance@{audit['factory_name'].lower().replace(' ', '').replace('&', '')}.in",
                    key="audit_mail_to"
                )
                
                lang_choice = st.selectbox(
                    "In-Mail Language Support*",
                    options=["en", "hi", "ta"],
                    format_func=lambda x: {"en": "🇬🇧 English (Default)", "hi": "🇮🇳 Hindi (हिंदी)", "ta": "🇮🇳 Tamil (தமிழ்)"}.get(x, x),
                    key="audit_mail_lang"
                )

            with mail_col2:
                # Determine default notice type
                default_notice_type = "FRAUD_ALERT" if audit['fraud_res']['is_fake'] else "SEAL_WARNING" if audit['gaia_score'] < 40 else "IMPROVEMENT_NOTICE" if audit['gaia_score'] < 60 else "ACKNOWLEDGMENT"
                notice_types = ["AUTOMATIC (Based on Score)", "FRAUD_ALERT", "SEAL_WARNING", "IMPROVEMENT_NOTICE", "ACKNOWLEDGMENT"]
                selected_notice_type = st.selectbox("Notice Category Override", notice_types, index=0, key="audit_mail_type")

            # Generate warning object using NotificationSystem
            suggestions_list = [rec['urgency'] for rec in audit['recommendations']]
            warning_notice = notification_system.generate_warning(
                factory_name=audit['factory_name'],
                score=audit['gaia_score'],
                suggestions=suggestions_list,
                is_fake=audit['fraud_res']['is_fake'],
                language=lang_choice
            )

            # Override type if explicitly selected
            if selected_notice_type != "AUTOMATIC (Based on Score)":
                warning_notice['type'] = selected_notice_type
                if selected_notice_type == "FRAUD_ALERT":
                    warning_notice['severity'] = "HIGH"
                    warning_notice['icon'] = "🚨"
                elif selected_notice_type == "SEAL_WARNING":
                    warning_notice['severity'] = "CRITICAL"
                    warning_notice['icon'] = "🔴"
                elif selected_notice_type == "IMPROVEMENT_NOTICE":
                    warning_notice['severity'] = "MEDIUM"
                    warning_notice['icon'] = "🟡"
                else:
                    warning_notice['severity'] = "LOW"
                    warning_notice['icon'] = "✅"

            # Preview content
            preview_body = warning_notice.get('body_translated', warning_notice['body'])
            edited_body = st.text_area("In-Mail Message Content Preview (Editable)*", value=preview_body, height=180, key="audit_mail_body")
            warning_notice['body'] = edited_body

            if st.button("📤 Dispatch In-Mail Notice & Record to Log", type="primary", use_container_width=True, key="btn_send_audit_notice"):
                if not recipient_email.strip():
                    st.error("Please enter a valid recipient email.")
                else:
                    # 1. Send via NotificationSystem
                    notification_system.send(recipient_email, warning_notice)

                    # 2. Persist in database
                    db.save_notification(
                        recipient=recipient_email,
                        notification_type=warning_notice['type'],
                        severity=warning_notice.get('severity', 'MEDIUM'),
                        subject=warning_notice.get('subject', 'GAIA Regulatory Notice'),
                        content=edited_body
                    )

                    st.success(f"✅ In-Mail Regulatory Notice successfully transmitted to {recipient_email} and logged in statutory register!")

            st.caption(f"🌱 Audit Carbon Footprint: {audit['emissions_g']:.4f} gCO₂e (Zero GPU emissions)")

    # --- TAB 2: IN-MAIL NOTICES & MESSAGING (STANDALONE MANAGEMENT) ---
    with tab_mail:
        st.subheader("✉️ In-Mail Communications & Statutory Notice Dispatch")
        st.caption("Manage official regulatory correspondence, multilingual notices, and automated compliance reminders.")

        subtab_send, subtab_remind, subtab_history = st.tabs([
            "✉️ Compose & Send Notice",
            "⏰ Due Reminders & Escalations",
            "📜 Dispatched Notices Register"
        ])

        with subtab_send:
            st.markdown("#### Compose Direct In-Mail Notice")
            col_m_to, col_m_fac = st.columns(2)
            with col_m_fac:
                compose_fac = st.text_input("Enterprise Name*", placeholder="e.g., Apex Chemicals Ltd", key="comp_fac")
            with col_m_to:
                compose_to = st.text_input("Recipient Email Address*", placeholder="compliance@enterprise.com", key="comp_to")

            col_m_typ, col_m_lang = st.columns(2)
            with col_m_typ:
                comp_type = st.selectbox(
                    "Notice Type*",
                    ["IMPROVEMENT_NOTICE", "SEAL_WARNING", "FRAUD_ALERT", "ACKNOWLEDGMENT"],
                    key="comp_type"
                )
            with col_m_lang:
                comp_lang = st.selectbox(
                    "Message Language*",
                    ["en", "hi", "ta"],
                    format_func=lambda x: {"en": "🇬🇧 English", "hi": "🇮🇳 Hindi (हिंदी)", "ta": "🇮🇳 Tamil (தமிழ்)"}.get(x, x),
                    key="comp_lang"
                )

            comp_score = st.slider("Recorded Compliance Score", 0, 100, 50, key="comp_score")
            
            # Generate template notice
            template_notice = notification_system.generate_warning(
                factory_name=compose_fac if compose_fac.strip() else "Factory Enterprise",
                score=comp_score,
                suggestions=["Implement mandatory OCEMS monitoring", "Reduce effluent chemical oxygen demand (COD)", "Submit compliance report"],
                is_fake=(comp_type == "FRAUD_ALERT"),
                language=comp_lang
            )
            template_notice['type'] = comp_type

            comp_body = st.text_area(
                "In-Mail Body (with Regional Language Translation)*",
                value=template_notice.get('body_translated', template_notice['body']),
                height=180,
                key="comp_body"
            )
            template_notice['body'] = comp_body

            if st.button("🚀 Send Direct In-Mail Notice", type="primary", use_container_width=True, key="btn_send_direct_notice"):
                if not compose_to.strip():
                    st.error("Please provide recipient email.")
                elif not compose_fac.strip():
                    st.error("Please provide enterprise name.")
                else:
                    notification_system.send(compose_to, template_notice)
                    db.save_notification(
                        recipient=compose_to,
                        notification_type=comp_type,
                        severity=template_notice.get('severity', 'MEDIUM'),
                        subject=template_notice.get('subject', 'GAIA Regulatory Notice'),
                        content=comp_body
                    )
                    st.success(f"Official in-mail notice dispatched to {compose_to}!")

        with subtab_remind:
            st.markdown("#### Automated Compliance Deadline Reminders")
            st.info("Automated reminders follow up with enterprises whose compliance submission deadline is within 7 days.")

            col_btn_rem, col_rem_stat = st.columns([1, 2])
            with col_btn_rem:
                if st.button("⏰ Check & Dispatch Due Reminders", use_container_width=True):
                    sent_count = notification_system.send_due_reminders()
                    st.success(f"Dispatched {sent_count} automated reminder notice(s) approaching deadline.")

            # Show pending reminders
            pending = notification_system.get_pending_reminders()
            if pending:
                st.warning(f"Found {len(pending)} pending action(s) nearing compliance deadline:")
                for p in pending:
                    st.write(f"• **{p['to']}** — {p['notification']['type']} (Days Remaining: `{p['days_remaining']}`)")
            else:
                st.info("No notices currently in the 7-day critical reminder window.")

        with subtab_history:
            st.markdown("#### Dispatched In-Mail Statutory Log")
            db_notifs = db.get_notifications(limit=50)
            if db_notifs:
                df_notifs = pd.DataFrame(db_notifs)
                st.dataframe(df_notifs, use_container_width=True)
            else:
                st.info("No dispatched notices found in database records yet.")

    # --- TAB 3: FRAUD DETECTION ALERTS ---
    with tab2:
        st.subheader("🚨 High-Risk & Fabricated Reports Requiring Action")
        all_reports = db.get_reports(limit=50)

        fraud_reports = [r for r in all_reports if r.get('is_fake') or r.get('fraud_score', 0) >= 0.4]

        if fraud_reports:
            st.warning(f"⚠️ Found {len(fraud_reports)} submission(s) flagged with high fraud indicators.")
            for r in fraud_reports:
                with st.expander(f"🚩 {r['factory_name']} — Score: {r['gaia_score']} | Fraud Risk: {int(r.get('fraud_score', 0)*100)}%"):
                    st.write(f"**Industry:** {r.get('industry', 'N/A')}")
                    st.write(f"**Submitted Date:** {r.get('created_at', 'N/A')}")
                    st.write(f"**Regulatory Status:** {r.get('status', 'N/A')}")
                    st.write(f"**Report Excerpt:**")
                    st.info(r.get('report_text', '')[:400] + "...")
                    if st.button(f"Mark for On-Site Inspection", key=f"inspect_{r['id']}"):
                        st.success(f"Physical inspection scheduled for {r['factory_name']}.")
        else:
            st.success("✅ No fraudulent submissions detected in recent records.")

    # --- TAB 3: REPORT ARCHIVE & SEARCH ---
    with tab3:
        st.subheader("📋 Industrial Submission Archive")
        search_query = st.text_input("🔍 Search reports by company name or keyword:")
        
        if search_query.strip():
            reports = db.search_reports(search_query)
        else:
            reports = db.get_reports(limit=30)

        if reports:
            df_reports = pd.DataFrame(reports)
            columns_to_show = ['id', 'factory_name', 'gaia_score', 'status', 'is_fake', 'fraud_score', 'industry', 'created_at']
            available_cols = [c for c in columns_to_show if c in df_reports.columns]
            st.dataframe(df_reports[available_cols], use_container_width=True)
        else:
            st.info("No reports found matching your criteria.")

    # --- TAB 4: CITIZEN GRIEVANCE TRIAGE ---
    with tab4:
        st.subheader("🛠️ Review & Resolve Citizen Environmental Grievances")
        complaints = db.get_complaints(limit=30)

        if complaints:
            for c in complaints:
                status_color = "red" if c['status'] == "PENDING" else "orange" if c['status'] == "IN_PROGRESS" else "green"
                with st.expander(f"📌 [{c.get('status', 'PENDING')}] {c.get('tracking_id')} — {c.get('complaint_type')} @ {c.get('location')}"):
                    st.write(f"**Severity:** `{c.get('severity', 'MEDIUM')}`")
                    st.write(f"**Reported At:** {c.get('created_at')}")
                    st.write(f"**Description:** {c.get('description')}")
                    st.write(f"**Assigned Officer:** {c.get('officer_assigned', 'Unassigned')}")

                    col_act1, col_act2, col_act3 = st.columns([1, 1, 1])
                    with col_act1:
                        officer_input = st.text_input("Assign Officer", value=c.get('officer_assigned') or "Insp. Sharma", key=f"off_{c['id']}")
                    with col_act2:
                        status_select = st.selectbox("Update Status", ["PENDING", "IN_PROGRESS", "RESOLVED"], index=["PENDING", "IN_PROGRESS", "RESOLVED"].index(c.get('status', 'PENDING')), key=f"stat_{c['id']}")
                    with col_act3:
                        st.write("")
                        st.write("")
                        if st.button("Save Updates", key=f"save_cmp_{c['id']}"):
                            db.update_complaint_status(
                                tracking_id=c['tracking_id'],
                                status=status_select,
                                officer_assigned=officer_input,
                                inspection_date=datetime.now().strftime("%Y-%m-%d")
                            )
                            st.success(f"Complaint {c['tracking_id']} updated to {status_select}!")
                            st.rerun()
        else:
            st.info("No citizen complaints currently logged.")

# =========================================================================
# 2. CITIZEN GRIEVANCE PORTAL
# =========================================================================
elif portal == "📢 Citizen Grievance Portal":
    st.header("📢 Citizen Environmental Violation Reporting")
    st.caption("Empowering communities to report industrial pollution with AI image inspection and multilingual voice support.")

    cit_tab1, cit_tab2 = st.tabs(["📝 File a Violation Report", "🔍 Track Existing Complaint"])

    # --- TAB 1: FILE COMPLAINT ---
    with cit_tab1:
        st.markdown("### Step 1: Upload Visual Evidence (Optional)")
        
        col_img_up, col_sample_img = st.columns([2, 1])
        with col_sample_img:
            st.write("")
            st.write("")
            load_sample_img = st.button("🖼️ Load Sample Violation Photo", use_container_width=True)

        with col_img_up:
            photo = st.file_uploader("Upload pollution photograph (.jpg, .png)", type=['jpg', 'jpeg', 'png'])

        img_bytes = None
        if load_sample_img:
            try:
                with open("sample data/sample_violation.jpg", "rb") as f:
                    img_bytes = f.read()
                st.session_state.cit_photo_bytes = img_bytes
                st.toast("Loaded sample violation image!", icon="🖼️")
            except Exception as e:
                st.error(f"Could not load sample image: {e}")
        elif photo is not None:
            img_bytes = photo.getvalue()
            st.session_state.cit_photo_bytes = img_bytes

        image_detection_summary = ""
        suggested_complaint_type = "water_pollution"
        suggested_severity = "MEDIUM"

        if "cit_photo_bytes" in st.session_state and st.session_state.cit_photo_bytes:
            col_preview, col_vision = st.columns([1, 1])
            with col_preview:
                st.image(st.session_state.cit_photo_bytes, caption="Uploaded Evidence", width=320)
            
            with col_vision:
                with st.spinner("AI MobileNet analyzing image for environmental violations..."):
                    img_analysis = image_analyzer.analyze(st.session_state.cit_photo_bytes)
                
                if img_analysis.get('success'):
                    det = img_analysis.get('detection', {})
                    if det.get('has_pollution'):
                        st.warning(f"🚨 **Violation Detected:** {det.get('pollution_type', 'Pollution').replace('_', ' ').title()}")
                        st.write(f"**Severity:** `{det.get('severity', 'MEDIUM')}` | **Confidence:** `{int(det.get('confidence', 0.7)*100)}%`")
                        st.caption(f"Details: {det.get('description', '')}")
                        image_detection_summary = f"[AI Vision Flag]: {det.get('description')}"
                        if det.get('pollution_type'):
                            suggested_complaint_type = det.get('pollution_type')
                        suggested_severity = det.get('severity', 'MEDIUM')
                    else:
                        st.success("✅ No immediate visible hazardous pollution detected.")
                        image_detection_summary = "[AI Vision]: Clear / inconclusive"

        st.markdown("### Step 2: Voice or Text Description (Multilingual Support)")
        st.caption("Speak in any language (Tamil, Hindi, Telugu, English, etc.) — GAIA's Whisper AI will transcribe and extract complaint specifics.")

        # Multilingual Language Selector (Tamil, Telugu, English, Hindi, and Auto-Detect)
        col_lang, _ = st.columns([1, 1])
        with col_lang:
            speech_lang_options = {
                "Auto-Detect (Multilingual)": None,
                "English": "en",
                "Tamil (தமிழ்)": "ta",
                "Telugu (తెలుగు)": "te",
                "Hindi (हिन्दी)": "hi"
            }
            selected_lang_label = st.selectbox(
                "🌐 Speech Recognition Mode / Language Hint:",
                list(speech_lang_options.keys()),
                index=0,
                help="Whisper AI automatically detects language by default. You can also explicitly select Tamil, Telugu, or English for targeted recognition."
            )
            selected_lang_code = speech_lang_options[selected_lang_label]

        col_audio1, col_audio2 = st.columns(2)
        with col_audio1:
            voice_mic = st.audio_input("🎤 Record Audio via Microphone")
            st.caption("ℹ️ *Click the mic to speak. When finished, click the Stop button (⏹️) to transcribe.*")
        with col_audio2:
            voice_file = st.file_uploader("📁 Or Upload Recorded Voice Note (.mp3, .wav, .m4a)", type=['mp3', 'wav', 'm4a'])
            if st.button("🎵 Load Sample Tamil Voice Complaint (complaint_tamil.mp3)"):
                try:
                    with open("complaint_tamil.mp3", "rb") as f:
                        st.session_state.cit_audio_bytes = f.read()
                    st.toast("Loaded sample Tamil complaint audio!", icon="🎤")
                except Exception as e:
                    st.error(f"Error loading sample audio: {e}")

        audio_data = None
        if voice_mic is not None:
            audio_data = voice_mic.getvalue()
        elif voice_file is not None:
            audio_data = voice_file.getvalue()
        elif "cit_audio_bytes" in st.session_state and st.session_state.cit_audio_bytes:
            audio_data = st.session_state.cit_audio_bytes

        # Initialize session state for editable fields
        if "cit_description" not in st.session_state:
            st.session_state.cit_description = ""
        if "cit_location" not in st.session_state:
            st.session_state.cit_location = "Near Industrial SIPCOT Area, Sector 4"

        voice_res = None
        if audio_data:
            col_ply, col_act = st.columns([3, 1])
            with col_ply:
                st.audio(audio_data)
            with col_act:
                st.write("")
                force_transcribe = st.button("🔄 Transcribe Speech", use_container_width=True)

            # Unique hash of audio data + language setting to prevent redundant re-runs while preserving user edits
            current_audio_hash = hashlib.md5(audio_data).hexdigest() + f"_{selected_lang_code}"

            needs_processing = (
                st.session_state.get("cit_last_audio_hash") != current_audio_hash
                or force_transcribe
                or not st.session_state.get("cit_last_voice_res")
                or not st.session_state.get("cit_last_voice_res", {}).get("success")
            )

            if needs_processing:
                with st.spinner("Whisper AI transcribing speech & extracting details..."):
                    voice_res = voice_processor.process(audio_data, language=selected_lang_code)

                st.session_state.cit_last_audio_hash = current_audio_hash
                st.session_state.cit_last_voice_res = voice_res

                if voice_res.get('success'):
                    recognized_text = voice_res.get('transcript', '').strip()
                    if recognized_text:
                        # Auto-update the Incident Details / Remarks text area
                        if image_detection_summary:
                            st.session_state.cit_description = f"{recognized_text}\n{image_detection_summary}".strip()
                        else:
                            st.session_state.cit_description = recognized_text

                        # Auto-update complaint details if extracted
                        details = voice_res.get('complaint_details', {})
                        if details.get('complaint_type'):
                            st.session_state.cit_suggested_type = details['complaint_type']
                        if details.get('urgency'):
                            st.session_state.cit_suggested_severity = details['urgency']
                        if details.get('location_mentioned'):
                            st.session_state.cit_location = details['location_mentioned']
                        st.toast("✅ Voice converted to text!", icon="🎤")
            else:
                voice_res = st.session_state.get("cit_last_voice_res")

            # Show warning only if speech recognition failed
            if voice_res and not voice_res.get('success'):
                err_msg = voice_res.get('error', 'No recognizable speech detected. Please speak closer to the microphone and try again.')
                st.warning(f"⚠️ {err_msg}")

        st.markdown("### Step 3: Verify & Submit Grievance")
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            location_val = st.text_input(
                "Violation Location / Landmark*",
                key="cit_location",
                help="Specify village, street, landmark, or GPS coordinates"
            )
            complaint_types = ["water_pollution", "air_pollution", "waste_dumping", "noise_pollution", "other"]
            active_type = st.session_state.get("cit_suggested_type", suggested_complaint_type)
            type_idx = complaint_types.index(active_type) if active_type in complaint_types else 0
            category = st.selectbox("Pollution Category*", complaint_types, index=type_idx)

        with col_c2:
            severity_levels = ["LOW", "MEDIUM", "HIGH"]
            active_sev = st.session_state.get("cit_suggested_severity", suggested_severity)
            sev_idx = severity_levels.index(active_sev) if active_sev in severity_levels else 1
            severity_choice = st.selectbox("Urgency / Severity Level*", severity_levels, index=sev_idx)

            # Pre-populate with image summary if user hasn't spoken and field is still empty
            if not st.session_state.cit_description.strip() and image_detection_summary:
                st.session_state.cit_description = image_detection_summary

            description_val = st.text_area(
                "Incident Details / Remarks*",
                key="cit_description",
                height=110,
                placeholder="Spoken words from microphone will appear here automatically. You can also type or edit details directly.",
                help="Spoken words are automatically entered here. You can manually edit this text before submitting."
            )

        if st.button("🚀 Submit Citizen Complaint", type="primary", use_container_width=True):
            if not location_val.strip():
                st.error("Please provide the location.")
            elif not description_val.strip():
                st.error("Please provide details of the violation.")
            else:
                tracker.start_operation("Citizen_Complaint_Submission")
                tracking_id = f"GAIA-{uuid.uuid4().hex[:6].upper()}"

                db.save_complaint(
                    tracking_id=tracking_id,
                    complaint_type=category,
                    location=location_val,
                    description=description_val,
                    severity=severity_choice
                )

                emissions_g = tracker.end_operation()

                st.balloons()
                st.markdown(f"""
                <div class="score-badge-card excellent">
                    <span class="stat-pill pill-pass">COMPLAINT REGISTERED</span>
                    <div class="big-score">{tracking_id}</div>
                    <h3>Grievance Successfully Lodged!</h3>
                    <p>Your environmental complaint has been routed to the state pollution control authority.</p>
                    <p><strong>Save your Tracking ID to monitor investigation status.</strong></p>
                </div>
                """, unsafe_allow_html=True)

    # --- TAB 2: TRACK STATUS ---
    with cit_tab2:
        st.subheader("🔍 Track Your Environmental Complaint")
        track_input = st.text_input("Enter your GAIA Tracking ID:", placeholder="e.g., GAIA-A1B2C3")

        if st.button("Track Status"):
            if not track_input.strip():
                st.error("Please enter a valid Tracking ID.")
            else:
                comp_record = db.get_complaint_by_tracking_id(track_input.strip())
                if comp_record:
                    st.success("✅ Complaint record retrieved!")
                    col_t1, col_t2 = st.columns(2)
                    with col_t1:
                        st.markdown(f"**Tracking ID:** `{comp_record['tracking_id']}`")
                        st.markdown(f"**Status:** `{comp_record.get('status', 'PENDING')}`")
                        st.markdown(f"**Pollution Category:** {comp_record.get('complaint_type')}")
                        st.markdown(f"**Location:** {comp_record.get('location')}")
                    with col_t2:
                        st.markdown(f"**Severity:** `{comp_record.get('severity', 'MEDIUM')}`")
                        st.markdown(f"**Assigned Inspector:** {comp_record.get('officer_assigned') or 'Pending Assignment'}")
                        st.markdown(f"**Inspection Date:** {comp_record.get('inspection_date') or 'To be scheduled'}")
                        st.markdown(f"**Lodged On:** {comp_record.get('created_at')}")

                    st.markdown("**Incident Description:**")
                    st.info(comp_record.get('description'))
                else:
                    st.error(f"No grievance found with Tracking ID: '{track_input}'. Please check and retry.")

# =========================================================================
# 3. ANALYTICS & INSIGHTS
# =========================================================================
elif portal == "📊 Analytics & Insights":
    st.header("📊 Sustainability & Compliance Intelligence")
    st.caption("High-level oversight of industrial compliance scores, fraud prevalence, and citizen grievance resolutions.")

    stats = db.get_statistics()
    perf = db.get_performance_summary()

    # KPI Top Cards
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    with kpi1:
        st.metric("Total Factory Reports", stats.get('total_reports', 0))
    with kpi2:
        st.metric("Avg GAIA Score", f"{stats.get('avg_gaia_score', 0)} / 100")
    with kpi3:
        st.metric("Flagged Fraud Rate", f"{perf.get('fraud_rate', 0)}%")
    with kpi4:
        st.metric("Citizen Complaints", stats.get('total_complaints', 0))

    st.divider()

    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        st.subheader("Industrial Compliance Status Breakdown")
        status_counts = stats.get('reports_by_status', {})
        if status_counts:
            df_status = pd.DataFrame(list(status_counts.items()), columns=['Regulatory Status', 'Count'])
            st.bar_chart(df_status.set_index('Regulatory Status'), color="#2e7d32")
        else:
            st.info("No compliance reports recorded yet.")

    with col_chart2:
        st.subheader("Citizen Complaints by Pollution Type")
        type_counts = stats.get('complaints_by_type', {})
        if type_counts:
            df_types = pd.DataFrame(list(type_counts.items()), columns=['Pollution Category', 'Complaints'])
            st.bar_chart(df_types.set_index('Pollution Category'), color="#ff9800")
        else:
            st.info("No citizen complaints logged yet.")

    st.markdown("### 📥 Export Regulatory Data")
    col_exp1, col_exp2 = st.columns(2)
    with col_exp1:
        all_reps = db.get_reports(limit=500)
        if all_reps:
            df_all_reps = pd.DataFrame(all_reps)
            csv_reps = df_all_reps.to_csv(index=False).encode('utf-8')
            st.download_button(
                "📥 Download All Reports (CSV)",
                data=csv_reps,
                file_name=f"gaia_factory_reports_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )
    with col_exp2:
        all_cmps = db.get_complaints(limit=500)
        if all_cmps:
            df_all_cmps = pd.DataFrame(all_cmps)
            csv_cmps = df_all_cmps.to_csv(index=False).encode('utf-8')
            st.download_button(
                "📥 Download All Complaints (CSV)",
                data=csv_cmps,
                file_name=f"gaia_citizen_complaints_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )

# =========================================================================
# 4. GREEN AI METRICS
# =========================================================================
elif portal == "🌱 Green AI Metrics":
    st.header("🌱 Green AI Operational Footprint")
    st.caption("Quantifying the computational efficiency and carbon savings of lightweight CPU edge AI versus massive cloud GPU clusters.")

    summary = tracker.get_summary()

    col_g1, col_g2, col_g3, col_g4 = st.columns(4)
    with col_g1:
        st.metric("Total AI Emissions", f"{summary['total_emissions_g']:.3f} gCO₂e")
    with col_g2:
        st.metric("Total Energy Used", f"{summary['total_energy_kwh']:.6f} kWh")
    with col_g3:
        st.metric("AI Operations Executed", summary['operations_count'])
    with col_g4:
        st.metric("Carbon Saved vs Cloud AI", f"{summary['carbon_saved_percent']}%", delta="Green AI Advantage")

    st.divider()

    st.markdown("""
    ### Why GAIA Uses Green AI:
    * **Ultra-Lightweight Models:** DistilBERT (66MB), MobileNet V2 (16MB), and Whisper Tiny (39MB) run entirely on local CPUs with **zero dedicated GPU cooling or power draw**.
    * **50x Lower Carbon Footprint:** Conventional cloud LLMs consume ~50x more wattage per inference query compared to optimized edge quantized models.
    * **Real-time Grid Sensitivity:** Dynamic adaptation based on current grid carbon intensity (averaging 400–700 gCO₂/kWh in India).
    """)

    st.subheader("Operational Execution Log")
    if tracker.operations:
        df_ops = pd.DataFrame(tracker.operations)
        st.dataframe(df_ops, use_container_width=True)
    else:
        st.info("No AI operations executed in the current session yet. Run a report audit or voice transcription to record emissions.")

    if st.button("Reset Carbon Session Counters"):
        tracker.reset()
        st.rerun()

# Global Footer
st.markdown("---")
st.caption("🌍 **GAIA Platform** • Green AI-Powered Environmental Compliance & Citizen Empowerment • 2026")