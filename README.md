# Three-Level Authentication System with Behavioral Analysis

### 🔐 Overview
This project demonstrates a **three-level authentication system** enhanced with **behavioral analysis** using Python.  
It’s designed to strengthen user authentication by combining:
1. **Basic credential verification** (Username & Password)  
2. **Image Clik** or **Color Sequence**  
3. **Behavioral biometric analysis** — such as keystroke dynamics, mouse movement, or typing speed.

---

## 🎯 Purpose
Traditional authentication methods (like passwords alone) are often vulnerable to phishing and hacking.  
By adding behavioral analysis as an additional layer, this system detects if a user behaves differently — indicating potential unauthorized access.

---

## ⚙️ Key Features
✅ **Three-Level Security** – Username/Password, OTP/Security Key, and Behavioral Biometrics  
✅ **Behavioral Analysis Model** – Uses ML algorithms to verify user’s typing or mouse movement pattern  
✅ **Flask-based Web Interface** (inferred from `app.py`) for easy interaction  
✅ **User Data Logging** – Tracks authentication attempts and user behavior metrics  
✅ **Configurable Thresholds** in `config.py` for tuning model sensitivity

---

## 🧩 Project Structure
```
Three-Level-Authentication-System-with-Behavioral-Analysis-using-Python-main/
│
├── app.py                      # Main entry point (Flask app)
├── config.py                   # Configuration (thresholds, model paths)
├── behavior_analysis.py        # ML model for analyzing behavioral patterns
│
├── app/
│   ├── __init__.py             # Flask app initialization
│   ├── routes.py               # Defines web routes for login, verification, etc.
│   ├── auth_utils.py           # Helper functions for authentication logic
│   ├── models.py               # Database or ML model definitions
│
├── requirements.txt            # Python dependencies
└── README.md                   # You are here 🙂
```

---

## 🖥️ Installation Guide

### 1️⃣ Clone or Download the Repository
```bash
git clone https://github.com/yourusername/Three-Level-Authentication-System.git
cd Three-Level-Authentication-System-with-Behavioral-Analysis-using-Python-main
```

### 2️⃣ Create a Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate      # On Windows
source venv/bin/activate     # On macOS/Linux
```

### 3️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

---

## 🚀 How to Run the Application

### Run the Flask App
```bash
python app.py
```
Then open your browser and go to:
```
http://127.0.0.1:5000/
```

---

## 🧠 How It Works

### 🔹 Level 1 – Basic Authentication
User enters username and password → verified using stored credentials in database or JSON.

### 🔹 Level 2 – OTP/Security Code
If Level 1 succeeds → a One-Time Password (OTP) or pre-set security question appears.

### 🔹 Level 3 – Behavioral Analysis
If Level 2 succeeds → the system monitors:
- Keystroke timings  
- Mouse movements or click intervals  
- Typing speed consistency  

Machine learning algorithms (possibly Logistic Regression or SVM) predict if the behavior matches the genuine user profile.

If the behavior score < threshold → access is denied, even if passwords are correct.

---

## 📊 Example Workflow
1. User logs in with credentials.  
2. System sends OTP to registered email/phone.  
3. User enters OTP.  
4. System records user typing/mouse data.  
5. Behavioral model checks pattern similarity.  
6. Access granted only if all three levels pass.

---

## 🧰 Technologies Used
- **Python 3.8+**
- **Flask** – for web interface  
- **scikit-learn / pandas / numpy** – for ML model training  
- **joblib or pickle** – for saving trained models  
- **HTML / CSS / JavaScript** – for frontend pages

---

## 🔍 Future Improvements
- Add deep learning models for behavior classification  
- Integrate webcam-based facial or gaze recognition  
- Store behavioral data securely in encrypted databases  
- Add an admin dashboard for monitoring login analytics

---

## 📜 License
This project is open-source and can be used for educational or research purposes.

---

## 🙌 Credits
Developed as part of an academic project on **Behavioral Biometrics and Secure Authentication**.

---
