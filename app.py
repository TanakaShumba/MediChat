import streamlit as st
import time
import pandas as pd
import re
import random
from datetime import datetime

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="MediChat Pro", page_icon="🏥", layout="wide")

# --- SESSION STATE SETUP ---
if "page" not in st.session_state:
    st.session_state.page = "register"
if "patient_data" not in st.session_state:
    st.session_state.patient_data = {}
if "messages" not in st.session_state:
    st.session_state.messages = []
if "clinic_records" not in st.session_state:
    st.session_state.clinic_records = []
if "ticket_number" not in st.session_state:
    st.session_state.ticket_number = None

# --- LOGIC ENGINE ---
def analyze_clinical_risk(text, age):
    text = text.lower()
    score = 0
    flags = []
    
    # Critical Keywords
    if re.search(r"(chest|heart|crush|squeeze|tight|breath|gasp|air|choke|stroke|faint|collapse)", text):
        score += 50
        flags.append("Critical Risk")
        
    # Moderate Keywords
    if re.search(r"(bleed|cut|wound|broke|fracture|fever|hot|temp|burn|vomit|pain)", text):
        score += 20
        flags.append("Acute Symptoms")

    # Age Risk
    if age >= 65 and score > 10:
        score += 15
        flags.append("Geriatric Risk")
    
    # Classification
    if score >= 50:
        return "RED", flags, "🚨 IMMEDIATE PRIORITY"
    elif score >= 15:
        return "YELLOW", flags, "⚠️ URGENT CARE"
    else:
        return "GREEN", flags, "✅ ROUTINE WAIT"

# --- SIDEBAR (ADMIN) ---
with st.sidebar:
    st.title("🏥 Clinic Admin")
    
    # BRANDING FEATURE
    uploaded_logo = st.file_uploader("Upload Clinic Logo", type=["png", "jpg"])
    if uploaded_logo:
        st.image(uploaded_logo, width=150)
    else:
        st.caption("Upload logo to customize")

    st.divider()
    
    if st.session_state.clinic_records:
        st.success(f"{len(st.session_state.clinic_records)} Patients Today")
        df = pd.DataFrame(st.session_state.clinic_records)
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Report (CSV)", csv, "shift_report.csv", "text/csv")

    if st.button("Reset Kiosk"):
        st.session_state.page = "register"
        st.session_state.messages = []
        st.session_state.ticket_number = None
        st.rerun()

# --- SCREEN 1: REGISTRATION ---
if st.session_state.page == "register":
    st.title("🏥 Patient Check-In")
    st.markdown("### Welcome. Please sign in.")
    
    with st.form("reg_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Full Name")
            age = st.number_input("Age", 0, 120)
        with col2:
            gender = st.selectbox("Gender", ["Male", "Female", "Other"])
            pain = st.slider("Pain Level (0-10)", 0, 10, 0)
            
        if st.form_submit_button("Begin Triage"):
            if name and age > 0:
                st.session_state.patient_data = {
                    "Name": name, "Age": age, "Gender": gender, "Pain": pain,
                    "CheckInTime": datetime.now().strftime("%H:%M:%S")
                }
                st.session_state.page = "chat"
                
                # Start Chat
                msg = f"Hello {name}. Please describe your main symptoms."
                st.session_state.messages.append({"role": "assistant", "content": msg})
                st.rerun()

# --- SCREEN 2: CHAT & TICKET ---
elif st.session_state.page == "chat":
    # If we already have a ticket, show the "Success" screen
    if st.session_state.ticket_number:
        st.success("Check-In Complete")
        
        col1, col2 = st.columns([1, 2])
        with col1:
            # THE DIGITAL TICKET
            st.title(f"#{st.session_state.ticket_number}")
            st.caption("Your Ticket Number")
            
            # Simulated QR Code
            st.image("https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=" + st.session_state.ticket_number)
            
        with col2:
            p_data = st.session_state.patient_data
            st.markdown(f"### 👤 {p_data['Name']}")
            st.info("Please show this screen to the receptionist.")
            st.warning("Estimated Wait: 15 Minutes")
            
        if st.button("Start New Patient"):
            st.session_state.page = "register"
            st.session_state.messages = []
            st.session_state.ticket_number = None
            st.rerun()
            
    else:
        # NORMAL CHAT
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                
        if prompt := st.chat_input("I have a headache..."):
            st.chat_message("user").write(prompt)
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            urgency, flags, status = analyze_clinical_risk(prompt, st.session_state.patient_data['Age'])
            
            # Generate Ticket
            ticket = f"{urgency[0]}-{random.randint(100,999)}"
            st.session_state.ticket_number = ticket
            
            # Save Record
            record = {
                "Ticket": ticket,
                "Name": st.session_state.patient_data['Name'],
                "Urgency": urgency,
                "Complaint": prompt,
                "Time": datetime.now().strftime("%H:%M:%S")
            }
            st.session_state.clinic_records.append(record)
            st.rerun()
