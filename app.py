import streamlit as st
import time
import pandas as pd
import re
import random
from datetime import datetime
from deep_translator import GoogleTranslator

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="MediChat Universal", page_icon="🏥", layout="wide")

# --- LIST OF SUPPORTED LANGUAGES (Top 20 for UI, but supports all) ---
LANGUAGES = {
    "English": "en",
    "Spanish": "es",
    "French": "fr",
    "German": "de",
    "Chinese (Simplified)": "zh-CN",
    "Hindi": "hi",
    "Arabic": "ar",
    "Portuguese": "pt",
    "Russian": "ru",
    "Japanese": "ja",
    "Korean": "ko",
    "Italian": "it",
    "Vietnamese": "vi",
    "Turkish": "tr",
    "Polish": "pl",
    "Ukrainian": "uk",
    "Swahili": "sw",
    "Tagalog": "tl",
    "Dutch": "nl",
    "Greek": "el"
}

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

# --- TRANSLATION FUNCTION ---
# This helper function translates text only if the language is not English
def t(text, target_lang_code):
    if target_lang_code == "en":
        return text
    try:
        return GoogleTranslator(source='auto', target=target_lang_code).translate(text)
    except:
        return text # Fallback to English if internet fails

# --- LOGIC ENGINE (Analyze in English) ---
def analyze_clinical_risk(text):
    text = text.lower()
    score = 0
    flags = []
    
    # We define keywords in ENGLISH only.
    # Because we translate user input to English before checking!
    
    # 1. Critical Risk
    if re.search(r"(chest|heart|crush|squeeze|tight|breath|gasp|air|choke|stroke|faint|collapse|unconscious)", text):
        score += 50
        flags.append("Critical Risk")
        
    # 2. Moderate Risk
    if re.search(r"(bleed|cut|wound|broke|fracture|fever|hot|temp|burn|vomit|pain|agony)", text):
        score += 20
        flags.append("Acute Symptoms")

    # 3. Infection/General
    if re.search(r"(cough|sneeze|runny|itch|rash|headache)", text):
        score += 5
        flags.append("General Symptoms")

    # Classification
    if score >= 50:
        return "RED", flags, "🚨 IMMEDIATE PRIORITY"
    elif score >= 15:
        return "YELLOW", flags, "⚠️ URGENT CARE"
    else:
        return "GREEN", flags, "✅ ROUTINE WAIT"

# --- SIDEBAR (ADMIN & LANGUAGE) ---
with st.sidebar:
    st.title("🌐 Settings")
    
    # LANGUAGE SELECTOR
    lang_name = st.selectbox("Select Language", list(LANGUAGES.keys()))
    lang_code = LANGUAGES[lang_name] # e.g., 'es' for Spanish
    
    st.divider()
    
    st.title("🏥 Admin")
    uploaded_logo = st.file_uploader("Logo", type=["png", "jpg"])
    if uploaded_logo:
        st.image(uploaded_logo, width=150)
    
    if st.session_state.clinic_records:
        st.success(f"{len(st.session_state.clinic_records)} Patients")
        df = pd.DataFrame(st.session_state.clinic_records)
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 CSV Report", csv, "shift_report.csv", "text/csv")

    if st.button("Reset / Nuevo"):
        st.session_state.page = "register"
        st.session_state.messages = []
        st.session_state.ticket_number = None
        st.rerun()

# --- SCREEN 1: REGISTRATION ---
if st.session_state.page == "register":
    # Translate UI Elements
    ui_title = t("Patient Check-In", lang_code)
    ui_welcome = t("Welcome. Please sign in below.", lang_code)
    ui_name = t("Full Name", lang_code)
    ui_age = t("Age", lang_code)
    ui_gender = t("Gender", lang_code)
    ui_pain = t("Pain Level (0-10)", lang_code)
    ui_btn = t("Begin Triage", lang_code)

    st.title(f"🏥 {ui_title}")
    st.markdown(f"### {ui_welcome}")
    
    with st.form("reg_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input(ui_name)
            age = st.number_input(ui_age, 0, 120)
        with col2:
            gender = st.selectbox(ui_gender, ["Male", "Female", "Other"])
            pain = st.slider(ui_pain, 0, 10, 0)
            
        if st.form_submit_button(ui_btn):
            if name and age > 0:
                st.session_state.patient_data = {
                    "Name": name, "Age": age, "Language": lang_name
                }
                st.session_state.page = "chat"
                
                # AI Greeting (Translated)
                base_msg = f"Hello {name}. Please describe your main symptoms."
                trans_msg = t(base_msg, lang_code)
                st.session_state.messages.append({"role": "assistant", "content": trans_msg})
                st.rerun()

# --- SCREEN 2: CHAT ---
elif st.session_state.page == "chat":
    # Translate UI Elements for this page
    ui_ticket_header = t("Check-In Complete", lang_code)
    ui_show_reception = t("Please show this screen to the receptionist.", lang_code)
    ui_wait = t("Estimated Wait: 15 Minutes", lang_code)
    ui_new_patient = t("Start New Patient", lang_code)
    ui_placeholder = t("Describe your symptoms...", lang_code)
    
    if st.session_state.ticket_number:
        st.success(ui_ticket_header)
        col1, col2 = st.columns([1, 2])
        with col1:
            st.title(f"#{st.session_state.ticket_number}")
            st.image("https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=" + st.session_state.ticket_number)
        with col2:
            st.markdown(f"### 👤 {st.session_state.patient_data['Name']}")
            st.info(ui_show_reception)
            st.warning(ui_wait)
            
        if st.button(ui_new_patient):
            st.session_state.page = "register"
            st.session_state.messages = []
            st.session_state.ticket_number = None
            st.rerun()
            
    else:
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                
        if prompt := st.chat_input(ui_placeholder):
            # 1. Show User's Original Input
            st.chat_message("user").write(prompt)
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # 2. TRANSLATE INPUT TO ENGLISH (The Logic Trick)
            # This allows us to check for "chest pain" even if they typed in Russian
            input_in_english = GoogleTranslator(source='auto', target='en').translate(prompt)
            
            # 3. Analyze Risk (using the English translation)
            urgency, flags, status_english = analyze_clinical_risk(input_in_english)
            
            # 4. Formulate Response (in English first)
            if urgency == "RED":
                response_base = f"{status_english}\n\nHigh Priority case detected. A nurse is being alerted immediately."
            elif urgency == "YELLOW":
                response_base = f"{status_english}\n\nSymptoms logged. Please take a seat in Zone B."
            else:
                response_base = f"{status_english}\n\nPlease proceed to the reception desk."
            
            # 5. TRANSLATE RESPONSE BACK TO USER'S LANGUAGE
            final_response = t(response_base, lang_code)
            
            # 6. Generate Ticket
            ticket = f"{urgency[0]}-{random.randint(100,999)}"
            st.session_state.ticket_number = ticket
            
            # Save Record (We save both original and English for the doctor!)
            record = {
                "Ticket": ticket,
                "Name": st.session_state.patient_data['Name'],
                "Language": lang_name,
                "Original Complaint": prompt,
                "Translated Complaint": input_in_english,
                "Urgency": urgency,
                "Time": datetime.now().strftime("%H:%M:%S")
            }
            st.session_state.clinic_records.append(record)
            
            # Assistant Message
            with st.chat_message("assistant"):
                st.markdown(final_response)
            st.session_state.messages.append({"role": "assistant", "content": final_response})
            time.sleep(2)
            st.rerun()
