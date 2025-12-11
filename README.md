# 🏥 MediChat: Universal AI Patient Triage System

**MediChat** is a multilingual patient intake kiosk designed to streamline emergency room and clinic operations. It bridges the communication gap between patients and medical staff by instantly translating symptoms from **20+ languages** into standardized clinical English for risk assessment.

## 🚀 Live Demo
[**Click here to try the Live App**](https://medichat-jtpygclbxqkgaatirfnwum.streamlit.app/)

## 🔑 Key Features
* **🌍 Universal Translation:** Uses `deep-translator` to instantly convert patient inputs (Spanish, Swahili, Mandarin, etc.) into English for analysis, then replies in the patient's native language.
* **🧠 Clinical Logic Engine:** Specific Keyword & Regex analysis to detect high-risk symptoms (Chest Pain, Stroke, Respiratory Distress) and assign Triage Priority (Red/Yellow/Green).
* **🎫 Digital Ticket System:** Generates a unique Ticket ID (`#R-921`) and QR Code for seamless handoff to reception staff.
* **👨‍⚕️ Admin Dashboard:** Secure backend for doctors to view live logs and export shift records as CSV files.

## 🛠️ Tech Stack
* **Python 3.9+**
* **Streamlit** (Frontend UI)
* **Deep-Translator** (Google Translate API Wrapper)
* **Pandas** (Data Management & CSV Export)

## 📦 How to Run Locally
```bash
git clone [https://github.com/TanakaShumba/MediChat.git](https://github.com/TanakaShumba/MediChat.git)
cd MediChat
pip install -r requirements.txt
streamlit run app.py
