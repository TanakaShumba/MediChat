import streamlit as st
import time
import pandas as pd
import re
from datetime import datetime

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="MediChat Pro", page_icon="🏥", layout="wide")

# --- SESSION STATE SETUP ---
if "page" not in st.session_state:
    st.session_state.page = "register" # Start at registration
if "patient_data" not in st.session_state:
    st.session_state.patient_data = {}
if "messages" not in st.session_state:
    st.session_state.messages = []
if "clinic_records" not in st.session_state:
    # This simulates a database of all patients seen today
    st.session_state.clinic_records = []

# --- ADVANCED LOGIC ENGINE (Regex) ---
def analyze_clinical_risk(text, age):
    text = text.lower()
    score = 0
    flags = []
    
    # 1. Critical Keywords (High Weight)
    # Regex allows us to catch "can't breathe", "cannot breathe", "hard to breathe"
    if re.search(r"(chest|heart|crush|squeeze|tight)", text):
        score += 50
        flags.append("Cardiovascular Risk")
    if re.search(r"(breath|gasp|air|choke)", text):
        score += 50
        flags.append("Respiratory Distress")
    if re.search(r"(stroke|faint|collapse|pass out|droop|slur)", text):
        score += 50
        flags.append("Neurological Risk")
        
    # 2. Moderate Keywords
    if re.search(r"(bleed|cut|wound|broke|fracture)", text):
        score += 20
        flags.append("Trauma/Bleeding")
    if re.search(r"(fever|hot|temp|burn|chill)", text):
        score += 15
        flags.append("Infection Signs")
    if re.search(r"(vomit|nausea|diarrhea|stomach)", text):
        score += 15
        flags.append("GI Symptoms")

    # 3. Age Risk Factor
    # Elderly patients with moderate symptoms get bumped up
    if age >= 65 and score > 10:
        score += 15
        flags.append("Age Risk Factor (65+)")
    
    # 4. Final Classification
    if score >= 50:
        return "RED", flags, "🚨 IMMEDIATE ATTENTION"
    elif score >= 15:
        return "YELLOW", flags, "⚠️ URGENT CARE"
    else:
        return "GREEN", flags, "✅ ROUTINE WAIT"

# --- SIDEBAR (ADMIN PANEL) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3063/3063176.png", width=80)
    st.title("Clinic Admin")
    
    if st.session_state.clinic_records:
        st.success(f"{len(st.session_state.clinic_records)} Patients Triage Today")
        
        # Convert list to DataFrame for download
        df = pd.DataFrame(st.session_state.clinic_records)
        
        # CSV Download Button (The "Sell" Feature)
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            "📥 Download Shift Report (CSV)",
            csv,
            "clinic_shift_report.csv",
            "text/csv",
            key='download-csv'
        )
    else:
        st.info("No patients processed yet.")

    if st.button("New Patient (Reset)"):
        st.session_state.page = "register"
        st.session_state.messages = []
        st.session_state.patient_data = {}
        st.rerun()

# --- SCREEN 1: REGISTRATION ---
if st.session_state.page == "register":
    st.title("🏥 Patient Check-In Kiosk")
    st.markdown("Please fill out your details to begin triage.")
    
    with st.form("reg_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Full Name")
            age = st.number_input("Age", min_value=0, max_value=120, step=1)
        with col2:
            gender = st.selectbox("Gender", ["Male", "Female", "Other"])
            pain = st.slider("Pain Level (0-10)", 0, 10, 0)
            
        submitted = st.form_submit_button("Start Triage Chat")
        
        if submitted:
            if name and age > 0:
                # Save Data
                st.session_state.patient_data = {
                    "Name": name, "Age": age, "Gender": gender, "Pain": pain,
                    "CheckInTime": datetime.now().strftime("%H:%M:%S")
                }
                # Move to Chat
                st.session_state.page = "chat"
                
                # Initial AI Message
                welcome_msg = f"Hello {name}. I see you marked your pain level at {pain}/10. Please describe your symptoms in detail."
                st.session_state.messages.append({"role": "assistant", "content": welcome_msg})
                st.rerun()
            else:
                st.error("Please enter a valid Name and Age.")

# --- SCREEN 2: TRIAGE CHAT ---
elif st.session_state.page == "chat":
    p_data = st.session_state.patient_data
    
    # Header showing patient info
    st.info(f"👤 **Patient:** {p_data['Name']} | 🎂 **Age:** {p_data['Age']} | 📉 **Pain:** {p_data['Pain']}/10")
    
    # Chat History
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            
    # Input Area
    if prompt := st.chat_input("Type symptoms here..."):
        # User Message
        st.chat_message("user").write(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # ANALYZE LOGIC
        urgency, flags, status_text = analyze_clinical_risk(prompt, p_data['Age'])
        
        # Formulate Response
        if urgency == "RED":
            response = f"{status_text}\n\nBased on your input, this is a **High Priority** case. A nurse is being alerted immediately."
        elif urgency == "YELLOW":
            response = f"{status_text}\n\nWe have logged your symptoms. Please take a seat in Zone B. Estimated wait: 15 mins."
        else:
            response = f"{status_text}\n\nYour vitals seem stable. Please proceed to the reception desk to complete paperwork."
            
        # Assistant Message
        with st.chat_message("assistant"):
            st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
        
        # SAVE RECORD TO DATABASE (Session State)
        # We only save the *first* major symptom description for the main report
        record = {
            "Name": p_data['Name'],
            "Age": p_data['Age'],
            "Urgency": urgency,
            "Primary Complaint": prompt,
            "Flags": ", ".join(flags),
            "Timestamp": p_data['CheckInTime']
        }
        st.session_state.clinic_records.append(record)
