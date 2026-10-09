# 🏢 Smart AI Complaint Management & Prediction System

A complete full-stack web application featuring **Machine Learning** models for fake grievance filtering, duplicate/repeat complaint detection, geospatial infrastructure hotspot mapping, post-resolution student reviews with sentiment analysis, and predictive maintenance cost forecasting.

---

## 🚀 Key Features Implemented

1. **Fake Complaint Detection (ML + NLP Ensemble)**:
   - Evaluates incoming complaint text in real-time.
   - Combines TF-IDF Vectorizer + Logistic Regression with character entropy, punctuation density, and spam pattern heuristics.
   - Flags suspicious tickets (e.g. gibberish, troll complaints, spam) with an AI confidence score and alerts admin.

2. **Repeat / Duplicate Complaint Detection**:
   - Compares incoming complaints against active or recently resolved tickets in the same hostel/wing/category.
   - Uses TF-IDF cosine similarity to link duplicates, track recurrent infrastructure failures, and prevent redundant work orders.

3. **Complaint Location & Detailed Description Display (Admin Bug Fixed)**:
   - Full room numbers, building/hostel blocks, and geographic coordinates are tracked.
   - In the Admin portal, the **Description** column is prominently displayed with full text, category badges, and admin note capabilities.

4. **Review & Rating After Resolution**:
   - When a ticket status transitions to `Resolved`, students can rate the quality of service (1 to 5 stars) and submit comments.
   - Automatically computes NLP sentiment (`Positive`, `Neutral`, `Negative`) for administrative audit.

5. **Hotspot Geospatial Mapping**:
   - Interactive OpenStreetMap (via Leaflet.js) rendering hostel blocks and problem clusters.
   - Dynamic risk scoring (`High Risk`, `Medium Risk`, `Low Risk`) weighted by severity, unresolved volume, and repeat frequencies.

6. **Maintenance Cost & Volume Forecasting (ML Regression)**:
   - Fits linear and polynomial trend models on historical monthly tickets and category expenditures.
   - Projects complaint volume and budget requirements (with confidence intervals) for upcoming months.

---

## 📂 Project Structure

```
complaint-system/
├── backend/
│   ├── app.py                     # Main Flask application entry point
│   ├── config.py                  # MySQL credentials & configuration
│   ├── database.py                # SQLAlchemy Models (User, Complaint, Review, etc.)
│   ├── seed.py                    # Initial seed data for hostels, users, and tickets
│   ├── setup_database.sql         # SQL script to create MySQL database
│   ├── requirements.txt           # Python dependencies
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py                # User registration & JWT login
│   │   ├── complaints.py          # Student ticket filing & review submission
│   │   ├── admin.py               # Admin dashboard, status updates & reports
│   │   └── ml.py                  # ML endpoints for fake/repeat/forecast APIs
│   └── services/
│       ├── __init__.py
│       ├── fake_detector.py       # Scikit-learn NLP fake complaint classifier
│       ├── repeat_detector.py     # Cosine similarity duplicate detector
│       ├── cost_forecaster.py     # Regression model for maintenance forecasting
│       ├── hotspot_analyzer.py    # Risk cluster index & geospatial aggregator
│       └── sentiment_analyzer.py  # Post-resolution review sentiment analysis
├── frontend/
│   └── index.html                 # Complete responsive UI (Student & Admin)
├── run_backend.bat                # Windows 1-click backend runner
├── run_frontend.bat               # Windows 1-click frontend runner
├── start_all.bat                  # One-click start for entire project
└── README.md                      # Documentation & deployment guide
```

---

## 🛠️ Step-by-Step Setup Guide

### Step 1: Ensure MySQL is Running
Make sure your MySQL server is running on port `3306`. Your configured credentials are:
- **Host**: `localhost`
- **User**: `root`
- **Password**: `1633`
- **Database**: `complaint_system`

If the database doesn't exist yet, open your MySQL Command Line or Workbench and run:
```sql
CREATE DATABASE IF NOT EXISTS complaint_system CHARACTER SET utf8mb4;
```
*(The Flask backend will automatically create all tables and seed sample data on first run!)*

---

### Step 2: Install Python Dependencies & Start Backend
Open PowerShell or Command Prompt, navigate to the `backend` folder and run:
```powershell
cd C:\Users\Yoges\.gemini\antigravity\scratch\complaint-system\backend
pip install -r requirements.txt
python app.py
```
> **Or simply double-click**: `run_backend.bat` in the project root!

The backend will start at: `http://localhost:5000`

---

### Step 3: Launch the Frontend
Double-click `run_frontend.bat` or open `frontend/index.html` in your web browser (Chrome, Edge, Firefox).

> **Or start everything in one click**: Double-click `start_all.bat`.

---

## 🔑 Default Login Credentials

### Administrator / Warden:
- **Email**: `admin@hostel.com`
- **Password**: `admin123`
- **Features**: Real-time stats, view full descriptions, change ticket status, review hotspots map, cost forecasting, audit student reviews.

### Demo Student:
- **Email**: `rahul@student.com`
- **Password**: `pass123`
- **Features**: File complaints with live AI fake check, view complaint statuses, rate resolved tickets with stars and feedback.

*(You can also click **Register** on the login page to create any new student or admin account!)*

---

## 🌐 Easy Deployment Options

### Option A: Local Network / Campus LAN
1. In `backend/app.py`, it already listens on `0.0.0.0:5000`.
2. Find your PC's local IP address (`ipconfig` in Command Prompt, e.g. `192.168.1.15`).
3. In `frontend/index.html`, set `const API_BASE = 'http://192.168.1.15:5000/api';`.
4. Anyone on the same Wi-Fi/hostel network can now access the system!

### Option B: Free Cloud Deployment (Render / Railway)
1. Push this folder to a GitHub repository.
2. In [Render.com](https://render.com) or [Railway.app](https://railway.app):
   - Create a free **MySQL** instance and copy the connection string.
   - Deploy the `backend` directory as a **Web Service** with build command `pip install -r requirements.txt` and start command `python app.py`.
   - Host `frontend/index.html` on GitHub Pages, Netlify, or Vercel with zero configuration.
