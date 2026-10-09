@echo off
title Smart Complaint System - Backend
echo ========================================================
echo Starting Smart Complaint System Backend (Flask + MySQL + ML)
echo ========================================================
echo.

cd /d "%~dp0backend"

echo Checking and installing Python dependencies...
python -m pip install -r requirements.txt

echo.
echo Starting Flask Server on http://localhost:5000...
echo.
python app.py

pause
