@echo off
echo ==============================================
echo       TravelFusion AI - Server Stopper
echo ==============================================
echo.
echo Stopping the Flask server...
taskkill /F /IM python.exe >nul 2>&1
echo.
echo Server stopped successfully!
echo You can now safely close all windows.
pause >nul
