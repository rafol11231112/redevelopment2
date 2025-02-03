@echo off
title Setup RE Development Server
color 0b

echo Installing required tools...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed! Please install Python from python.org
    pause
    exit
)

REM Install ngrok if not present
if not exist "ngrok.exe" (
    echo Downloading ngrok...
    powershell -Command "Invoke-WebRequest -Uri 'https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-windows-amd64.zip' -OutFile 'ngrok.zip'"
    powershell -Command "Expand-Archive -Path 'ngrok.zip' -DestinationPath '.'" 
    del ngrok.zip
)

echo.
echo Please enter your ngrok authtoken (get it from dashboard.ngrok.com):
set /p token="> "
ngrok config add-authtoken %token%

echo.
echo Setup complete! Run start_server.bat to start the server.
echo.
pause 