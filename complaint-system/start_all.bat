@echo off
title Smart AI Complaint System - Quick Launcher
echo ========================================================
echo   SMART AI COMPLAINT PREDICTION & MANAGEMENT SYSTEM
echo ========================================================
echo.
echo 1. Launching Backend Server in separate window...
start "Backend (Flask & ML)" "%~dp0run_backend.bat"

echo.
echo 2. Waiting 3 seconds for server boot...
timeout /t 3 /nobreak >nul

echo.
echo 3. Launching Frontend Portal in your default browser...
start "" "%~dp0frontend\index.html"

echo.
echo System started successfully!
echo Backend API: http://localhost:5000
echo Frontend: opened in your default web browser
echo.
pause
