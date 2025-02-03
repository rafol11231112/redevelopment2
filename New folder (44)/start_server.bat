@echo off
title RE Development Server Startup
color 0b

echo Starting Python server and ngrok...
echo.

REM Start Python server in background
start python server.py

echo Waiting for server to start...
timeout /t 3 /nobreak >nul

REM Start ngrok
echo Starting ngrok tunnel...
ngrok http 8000

echo.
echo Press any key to shutdown servers...
pause >nul

REM Cleanup
taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM ngrok.exe >nul 2>&1 