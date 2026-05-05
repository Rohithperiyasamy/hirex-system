<div align="center">
  <img src="https://github.com/user-attachments/assets/fcbccd5c-4b79-4c7f-b143-3fa2a9fe33d1" alt="Evalio Banner" width="100%"/>
  
  # Evalio - AI Technical Interviewer
  
  *Revolutionizing Technical Hiring with Artificial Intelligence*
  
  ![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
  ![Django](https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white)
  ![JavaScript](https://img.shields.io/badge/javascript-%23323330.svg?style=for-the-badge&logo=javascript&logoColor=%23F7DF1E)
  ![HTML5](https://img.shields.io/badge/html5-%23E34F26.svg?style=for-the-badge&logo=html5&logoColor=white)
  ![CSS3](https://img.shields.io/badge/css3-%231572B6.svg?style=for-the-badge&logo=css3&logoColor=white)
  ![TailwindCSS](https://img.shields.io/badge/tailwindcss-%2338B2AC.svg?style=for-the-badge&logo=tailwind-css&logoColor=white)
  ![SQLite](https://img.shields.io/badge/sqlite-%2307405e.svg?style=for-the-badge&logo=sqlite&logoColor=white)
  ![Ollama](https://img.shields.io/badge/Ollama-000000.svg?style=for-the-badge&logo=ollama&logoColor=white)
  
</div>

## 🚀 Overview

Evalio is a cutting-edge AI-powered technical interview platform that streamlines the hiring process for companies. It conducts automated technical interviews, provides real-time candidate assessment, and generates comprehensive reports to help HR teams make informed hiring decisions.

## ✨ Key Features

### 🤖 AI-Powered Interviews
- **Dynamic Question Generation**: AI adapts questions based on job requirements and candidate responses
- **Real-time Speech Recognition**: Natural conversation with advanced speech analysis using Web Speech API
- **Voice Synthesis**: AI interviewer with natural speech capabilities
- **LLaMA 3.2 Integration**: Powered by Ollama for intelligent conversation flow

### 📊 Comprehensive Analytics
- **Performance Metrics**: Evaluates accuracy, communication, technical depth, and cultural fit
- **Bias Reduction**: Standardized evaluation criteria to minimize unconscious bias
- **Detailed Reports**: Comprehensive candidate assessments with hiring recommendations
- **PDF Report Generation**: Downloadable detailed assessment reports

### 🔒 Security & Monitoring
- **Automated Proctoring**: Real-time monitoring with face detection and malpractice detection
- **Secure Access**: Token-based authentication with session management
- **Image Analysis**: OpenCV-based face detection for interview integrity

### 📋 Management Features
- **Candidate Pipeline**: Upload and manage candidates via Excel files
- **Interview Scheduling**: Automated scheduling with email notifications
- **Dashboard Analytics**: Monitor all interviews and candidate progress through [Templates/dashboard.html](Templates/dashboard.html)
- **Feedback System**: Post-interview feedback collection via [Templates/feedback.html](Templates/feedback.html)

## 🛠️ Tech Stack

- **Backend**: Django (Python 3.x)
- **Frontend**: HTML5, CSS3, JavaScript, TailwindCSS
- **Database**: SQLite
- **AI/ML**: Ollama (LLaMA 3.2) / Gemini API 
- **Speech Processing**: Web Speech API (webkitSpeechRecognition)
- **Computer Vision**: OpenCV for proctoring
- **File Processing**: PyMuPDF for PDF handling
- **Authentication**: Django Authentication System

## 📁 Project Structure

```
Evalio/
├── Authentication/          # User authentication module
│   ├── models.py
│   ├── views.py
│   └── urls.py
├── Hr/                     # HR management functionality
│   ├── models.py
│   ├── views.py
│   └── urls.py
├── Myapp/                  # Core application logic
│   ├── models.py          # Database models
│   ├── views.py           # Application views
│   ├── utils.py           # AI utilities and evaluation functions
│   └── urls.py            # URL routing
├── Templates/             # HTML templates
│   ├── homepage.html      # Landing page
│   ├── dashboard.html     # HR dashboard
│   ├── interview.html     # Interview interface
│   ├── feedback.html      # Post-interview feedback
│   ├── ResultReport.html  # Assessment reports
│   ├── login.html         # Authentication pages
│   └── updatedSignup.html
├── Evalio/               # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── db.sqlite3            # Database file
├── manage.py             # Django management script
├── requirements.txt      # Python dependencies
└── README.md
```

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- pip (Python package manager)
- Git
- Ollama (for local AI model hosting)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/evalio.git
   cd evalio
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up Ollama and LLaMA 3.2**
   ```bash
   # Install Ollama
   curl -fsSL https://ollama.ai/install.sh | sh
   
   # Pull LLaMA 3.2 model
   ollama pull llama3.2
   ```

5. **Set up database**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run the development server**
   ```bash
   python manage.py runserver
   ```

8. **Access the application**
   - Open your browser and navigate to `http://127.0.0.1:8000/`

## 📖 Usage

### For HR Managers

1. **Sign Up/Login**: Create an HR account using [Templates/updatedSignup.html](Templates/updatedSignup.html)
2. **Dashboard Access**: Use [Templates/dashboard.html](Templates/dashboard.html) to manage interviews
3. **Upload Candidates**: Import candidate information via Excel files
4. **Schedule Interviews**: System automatically schedules and sends email invitations
5. **Monitor Progress**: Track interview completion and review analytics
6. **Generate Reports**: Download detailed PDF reports via [Templates/ResultReport.html](Templates/ResultReport.html)

### For Candidates

1. **Receive Invitation**: Get email invitation with unique interview link
2. **Join Interview**: Access [Templates/interview.html](Templates/interview.html) to start the AI interview
3. **Complete Assessment**: Answer questions naturally through voice interaction
4. **Automated Proctoring**: System monitors interview integrity using computer vision
5. **Provide Feedback**: Submit post-interview feedback via [Templates/feedback.html](Templates/feedback.html)

## 🔧 Configuration

### AI Model Setup
The evaluation system is configured in [`Myapp/utils.py`](Myapp/utils.py):
- Configure Ollama endpoint for LLaMA 3.2
- Customize evaluation criteria and scoring metrics
- Set required skills and nice-to-have skills for technical evaluation

### Proctoring System
Automated proctoring features include:
- Face detection using OpenCV
- Malpractice detection through image analysis
- Real-time monitoring during interviews

## 📊 Evaluation Methodology

The AI evaluation system assesses candidates across multiple dimensions:

1. **Accuracy**: Relevance of answers to questions asked
2. **Communication**: Clarity and elaboration in responses  
3. **Technical Depth**: Presence of domain-specific terminology
4. **Cultural/Role Fit**: Alignment with job requirements

Each metric is calculated using sophisticated algorithms detailed in the [`info.txt`](info.txt) documentation.

## 🎯 Key Features Breakdown

### Interview Process
- **Dynamic Questioning**: AI adapts questions based on candidate responses
- **Speech Recognition**: Real-time transcription and analysis
- **Voice Synthesis**: Natural AI interviewer voice
- **Session Management**: Token-based secure interview sessions

### Analytics & Reporting
- **Performance Metrics**: Comprehensive candidate evaluation
- **PDF Generation**: Professional interview reports
- **Dashboard Insights**: Real-time analytics for HR teams
- **Feedback Collection**: Post-interview candidate feedback

### Security Features
- **Proctoring System**: Computer vision-based monitoring
- **Secure Authentication**: Django-based user management
- **Session Tokens**: Secure interview access control

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Team

**Developed by:**
- Akash Kumar Gupta (10800221055)
- Samarjit Banerjee (10800221056)
- Pritam Sarbajna (10800222135)
- Md Athar Ansari (10800222137)

**Under the guidance of:**
- Dr. Sheuli Chakraborty, Assistant Professor, HOD Dept of CSBS
- Information Technology, Asansol Engineering College

## 🙏 Acknowledgments

- **Asansol Engineering College** for providing the platform for this project
- **Ollama** for local AI model hosting capabilities
- **Django Community** for the robust web framework
- **TailwindCSS** for responsive design
- **OpenCV** for computer vision capabilities

## 📞 Support

For support and questions:
- Email: banerjeesamarjit9@gmail.com
- Issues: [GitHub Issues](https://github.com/MrSamarjitBanerjee/Evalio/issues)
- Documentation: See [info.txt](info.txt) for detailed project information

---

<div align="center">
  <p>Made with ❤️ by the Evalio Team</p>
  <p>© 2025 Evalio Inc. All rights reserved.</p>
  
  **Asansol Engineering College | Information Technology Department**
</div>
#   h i r e x - s y s t e m  
 