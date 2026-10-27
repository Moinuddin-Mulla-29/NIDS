@echo off
title AI-NIDS Frontend Dashboard
cd /d "%~dp0frontend"
echo ========================================================
echo    Starting AI-NIDS React Dashboard (Port 5173)
echo ========================================================
npm run dev
pause
