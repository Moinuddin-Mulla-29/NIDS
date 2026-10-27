@echo off
title AI-NIDS Launcher
cd /d "%~dp0"
echo ========================================================
echo        Launching AI-NIDS SOC Detection System
echo ========================================================
echo [1/2] Starting Backend Server on http://127.0.0.1:8000 ...
start "AI-NIDS Backend" cmd /c "start_backend.bat"

echo [2/2] Starting Frontend Dashboard on http://localhost:5173 ...
start "AI-NIDS Frontend" cmd /c "start_frontend.bat"

echo.
echo Waiting for servers to initialize...
timeout /t 3 /nobreak >nul
echo Opening AI-NIDS Dashboard in your default browser...
start http://localhost:5173

echo.
echo [+] AI-NIDS is up and running!
echo [+] Backend API: http://127.0.0.1:8000 (Swagger docs at /docs)
echo [+] SOC Dashboard: http://localhost:5173
echo.
pause
