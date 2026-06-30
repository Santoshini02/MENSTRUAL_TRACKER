# 🌸 Menstrual Tracker — College Project

A Flask-based web application for tracking menstrual cycles, predicting future periods, logging symptoms, and generating personalized health reports.

## 🌐 Live Demo
Try it here: https://menstrual-tracker-yv60.onrender.com

## Tech Stack
- **Frontend:** HTML, CSS, JavaScript, Chart.js
- **Backend:** Python (Flask)
- **Database:** SQLite
- **PDF:** ReportLab

---

## ✨ Features
- User Registration & Login
- Track menstrual cycle data
- Predict upcoming periods
- Symptom logging
- Health tips & AI guide
- Analytics and trend charts
- Download PDF health report

---

## Setup Instructions (VS Code)

### 1. Install Python Dependencies
```bash
pip install flask reportlab
```

### 2. Run the Application
```bash
cd menstrual_tracker
python app.py
```

### 3. Open in Browser
```
http://127.0.0.1:5000
```

The database (`tracker.db`) is created automatically on first run.

---

## Project Structure
```
menstrual_tracker/
├── app.py                  # Flask backend (all routes + logic)
├── requirements.txt        # Dependencies
├── tracker.db              # SQLite database (auto-created)
└── templates/
    ├── base.html           # Shared layout with sidebar
    ├── login.html          # Login page
    ├── register.html       # Registration page
    ├── dashboard.html      # Main dashboard
    ├── calendar.html       # Visual calendar
    ├── trends.html         # Analytics charts
    ├── symptoms.html       # Symptom tracking
    ├── health.html         # Health tips
    ├── ai.html             # AI guide + chatbot
    ├── profile.html        # User profile + PDF download
    └── edit_cycle.html     # Edit cycle record
```

---

## Data Privacy
Every database query is filtered by `user_id` from the session. No cross-user data leakage.

## PDF Report
Visit `/download_report` or click "Download Report" from Dashboard/Profile.
Requires `reportlab`: `pip install reportlab`

---

## 🚀 Future Improvements
- Email reminders for periods
- Mobile app version
- Better AI assistant
- Doctor consultation support
- Cloud database integration

---

## 👩‍💻 Author
**Santoshini Nahak**  

## 📜 License
This project is created for educational and academic purposes.
