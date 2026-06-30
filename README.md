# 🌸 Menstrual Tracker — College Project

## Tech Stack
- **Frontend:** HTML, CSS, JavaScript, Chart.js
- **Backend:** Python (Flask)
- **Database:** SQLite
- **PDF:** ReportLab

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
