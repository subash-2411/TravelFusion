@echo off
echo ==============================================
echo       TravelFusion AI - Server Launcher
echo ==============================================
echo.

echo [1/3] Cleaning up old processes...
taskkill /F /IM python.exe >nul 2>&1
timeout /t 2 /nobreak >nul

echo [2/3] Opening launcher...
start index.html

echo [3/3] Starting the Flask server...
python app.py

echo.
echo Server stopped. Press any key to exit.
pause >nul

