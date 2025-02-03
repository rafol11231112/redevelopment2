@echo off
title RE Development Server
color 0b

echo Starting server...
start python server.py
timeout /t 2 >nul

echo Starting ngrok...
start ngrok http 8000

echo Server is running! Check the ngrok window for your URL.
echo Press any key to stop the server...
pause >nul

taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM ngrok.exe >nul 2>&1 