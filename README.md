

# Hirex — AI-Powered Automated Technical Interview System

> *An IoT-Based AI Interview Platform with Real-Time Assessment and Secure Proctoring*

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Django](https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white)
![JavaScript](https://img.shields.io/badge/javascript-%23323330.svg?style=for-the-badge&logo=javascript&logoColor=%23F7DF1E)
![HTML5](https://img.shields.io/badge/html5-%23E34F26.svg?style=for-the-badge&logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/css3-%231572B6.svg?style=for-the-badge&logo=css3&logoColor=white)
![Google Gemini](https://img.shields.io/badge/Google%20Gemini-8E75B2?style=for-the-badge&logo=googlegemini&logoColor=white)
![Ollama](https://img.shields.io/badge/Ollama-000000?style=for-the-badge&logo=ollama&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white)
![Raspberry Pi](https://img.shields.io/badge/Raspberry_Pi-C51A4A?style=for-the-badge&logo=Raspberry-Pi&logoColor=white)
![SQLite](https://img.shields.io/badge/sqlite-%2307405e.svg?style=for-the-badge&logo=sqlite&logoColor=white)

---

## 🚀 Overview

**Hirex** is an end-to-end AI-powered automated technical interview platform built with **Django (Python)** and **Large Language Models** (LLaMA 3.2 via Ollama / Google Gemini 1.5 Flash). It conducts fully voice-driven technical interviews, evaluates candidates in real time across multiple dimensions, and enforces interview integrity through a **dual-layer proctoring system** — OpenCV-based software proctoring in the browser and hardware-level monitoring via **Raspberry Pi 3 with Camera Module 3**.

Submitted as final year MCA project at **Muthayammal Engineering College (Autonomous), Anna University** — April 2026.

---

## ✨ Key Features

### 🤖 AI Interview Engine
- **Adaptive Question Generation** — LLaMA 3.2 (local via Ollama) or Gemini 1.5 Flash (cloud fallback) generates context-aware follow-up questions based on the candidate's resume, job role, and conversation history
- **Voice-Driven Interface** — `webkitSpeechRecognition` for candidate speech input; `SpeechSynthesis` API for AI voice output — no page reloads, fully conversational
- **Resume Parsing** — PyMuPDF (`fitz`) extracts text from Google Drive-hosted resume PDFs at session start
- **10-Round Structured Interview** — automatically terminates after 10 exchanges and triggers evaluation
- **Dual AI Provider with Auto-Fallback** — seamlessly switches between Ollama and Gemini on connection failure

### 🔒 Dual-Layer Proctoring
- **Software Proctoring** — browser captures webcam frames via HTML5 Canvas every 5 seconds, sends as base64 to Django backend for OpenCV Haar Cascade face detection
- **IoT Hardware Proctoring** — Raspberry Pi 3 with Camera Module 3 runs an independent Python script using `Picamera2` + OpenCV, sends authenticated violation events to `/iot/event/` via HTTP POST
- **Violation Scoring** — `>3` multiple-face frames → `cheating`; `>5` face-absent frames → `suspicious`; all events timestamped and logged to SQLite

### 📊 Evaluation & Reporting
- **Multi-Dimensional Scoring** — Accuracy (word overlap %), Communication (Low/Medium/High by word count), Technical Depth (30+ skill keyword matches), Good Fit (≥3 required skills mentioned)
- **AI-Generated Strengths & Weaknesses** — separate LLM call on full transcript, parsed into 3 bullet points each
- **PDF Report Generation** — PyMuPDF draws A4 reports with candidate info, metrics table, and complete IoT violation log; generated in under 1.2 seconds
- **HR Dashboard** — live pipeline with candidate status, proctoring scores, and one-click report download

### 🛠️ HR Management
- **Excel Bulk Upload** — `pandas.read_excel()` processes candidate data (Name, Email, Job Role, Experience, Resume Link)
- **Automated Scheduling** — slots filled 7 days ahead, up to 3 candidates/hour between 9AM–9PM
- **Email Invitations** — unique 32-character token links dispatched via Django + Gmail SMTP
- **OTP-Verified HR Registration** — 6-digit OTP with 5-minute expiry, PBKDF2-SHA256 password hashing

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Django 5.1 (Python 3.10+) |
| **AI / LLM (Local)** | Ollama with LLaMA 3.2 |
| **AI / LLM (Cloud Fallback)** | Google Gemini 1.5 Flash API |
| **Speech Processing** | Web Speech API (browser-native) |
| **Computer Vision** | OpenCV 4.x (Haar Cascade) |
| **PDF Processing** | PyMuPDF (fitz) 1.25+ |
| **IoT Hardware** | Raspberry Pi 3 Model B + Camera Module 3 |
| **Database** | SQLite via Django ORM |
| **Data Processing** | pandas (Excel upload) |
| **Frontend** | Django Templates, HTML5, CSS3, JavaScript |
| **Auth** | Token-based (secrets.token_hex) + OTP + Django sessions |

---

## 📁 Project Structure

```
hirex-system/
├── Authentication/         # HR registration, OTP verification, login/logout
│   ├── models.py
│   ├── views.py
│   └── urls.py
├── Hr/                     # HR dashboard, candidate scheduling, report download
│   ├── models.py
│   ├── views.py            # download_report_pdf(), schedule_next_interview()
│   └── urls.py
├── Myapp/                  # Core interview engine, proctoring, evaluation
│   ├── models.py           # interviewSchedule, IoTViolation, Feedback
│   ├── views.py            # tool(), iot_event(), join()
│   ├── utils.py            # ai_response(), generate(), pdf_ocr(), evaluation()
│   └── urls.py
├── Hirex/                  # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── Templates/              # Django HTML templates
│   ├── interview.html      # Voice interview UI with live waveform
│   ├── dashboard.html      # HR dashboard
│   ├── ResultReport.html   # Evaluation results view
│   ├── feedback.html       # Post-interview candidate feedback
│   └── login.html
├── iot_proctor.py          # Raspberry Pi proctoring script (Picamera2 + OpenCV)
├── db.sqlite3
├── manage.py
├── requirements.txt
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- pip
- [Ollama](https://ollama.ai) installed with LLaMA 3.2 pulled
- Google Gemini API key (for cloud fallback)
- Raspberry Pi 3 with Camera Module 3 (optional — for full IoT proctoring)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Rohithperiyasamy/hirex-system.git
   cd hirex-system
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate        # Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables** — create a `.env` file:
   ```env
   SECRET_KEY=your-django-secret-key
   EMAIL_HOST_USER=your@gmail.com
   EMAIL_HOST_PASSWORD=your-app-password
   GEMINI_API_KEY=your-gemini-api-key
   IOT_SECRET_KEY=hirex-iot-secret
   AI_PROVIDER=ollama          # or 'gemini'
   OLLAMA_MODEL=llama3.2:latest
   ```

5. **Pull LLaMA 3.2 via Ollama**
   ```bash
   ollama pull llama3.2
   ```

6. **Set up the database**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

7. **Run the server**
   ```bash
   python manage.py runserver
   ```

8. **Access the application**
   - HR Portal: `http://127.0.0.1:8000/auth/login/`
   - HR Dashboard: `http://127.0.0.1:8000/hr/dashboard/`

### IoT Proctoring Setup (Raspberry Pi)

```bash
# On the Raspberry Pi
pip install picamera2 opencv-python requests
# Edit HIREX_URL and CANDIDATE_TOKEN in iot_proctor.py
python iot_proctor.py
```

---

## 📊 Evaluation Methodology

After 10 interview rounds, the `evaluation()` function scores candidates across four dimensions:

| Metric | Method |
|---|---|
| **Accuracy** | Word overlap between candidate answers and interviewer questions (%) |
| **Communication** | Word count classification — ≤3: Low, 4–60: Medium, >60: High |
| **Technical Depth** | Count of 30+ domain skill keywords found across all answers |
| **Good Fit** | True if ≥3 required skills mentioned |

Strengths and weaknesses are separately generated by an LLM call on the full transcript.

---

## 🗄️ Database Schema

Three core models:
- **`Hr`** — HR account with hashed password, OTP fields, session key
- **`interviewSchedule`** — candidate info, secure token, scheduled time, all evaluation scores, IoT violation log (JSON), proctoring score
- **`Feedback`** — candidate post-interview rating and comments (FK → interviewSchedule)

---

## 🎓 Academic Details

**Project Title**: An IoT Based AI-Powered Automated Technical Interview System with Real-Time Assessment and Secure Proctoring  
**Degree**: Master of Computer Applications (MCA)  
**Institution**: Muthayammal Engineering College (Autonomous), Rasipuram — Anna University  
**Project Period**: January 2026 – April 2026  
**Guide**: Mrs. C. Radha, MCA., M.Phil.

---

## 🔮 Future Enhancements

- LPWAN (NB-IoT / LoRa) support for Raspberry Pi in low-WiFi environments
- Emotion and stress analysis using DeepFace on IoT camera frames
- Live coding assessment module (Monaco / CodeMirror editor)
- Migration from SQLite to PostgreSQL for multi-user production deployment
- ATS integration (Zoho Recruit, Greenhouse) via API

---

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/YourFeature`)
3. Commit your changes (`git commit -m 'Add YourFeature'`)
4. Push to the branch (`git push origin feature/YourFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

## 👤 Author

**Rohith P** (Reg. No.: 24MC024)  
MCA Final Year | Muthayammal Engineering College, Anna University  
📧 rohithperiyasamy7@gmail.com  
🔗 [linkedin.com/in/rohith74](https://linkedin.com/in/rohith74) | [github.com/Rohithperiyasamy](https://github.com/Rohithperiyasamy)

---

*Built with Python, patience, and a Raspberry Pi that actually worked.*




<div align="center">
  <p>Made with ❤️ by Rohith P</p>
  <p>© 2026 Hirex Inc. All rights reserved.</p>
  
  **Muthayammal Engineering College | MCA Department**
</div>
#   h i r e x - s y s t e m 
 
 
