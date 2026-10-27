@echo off
title AI-NIDS Backend Server
cd /d "%~dp0"
echo ========================================================
echo    Starting AI-NIDS FastAPI Backend (Port 8000)
echo ========================================================
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
pause
