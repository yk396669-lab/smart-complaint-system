@echo off
title Smart Complaint System - Frontend
echo ========================================================
echo Opening Smart Complaint Management Frontend in Browser...
echo ========================================================
echo.

cd /d "%~dp0frontend"
start index.html

echo Frontend launched! You can also serve it using Python:
echo python -m http.server 3000
echo.
pause
