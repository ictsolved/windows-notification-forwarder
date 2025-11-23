@echo off
REM Windows Notification Forwarder - Startup Script
REM This script starts the notification forwarder application

echo ============================================================
echo Windows Notification Forwarder
echo ============================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH!
    echo.
    echo Please install Python 3.8+ from https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

REM Check if .env file exists
if not exist ".env" (
    echo ERROR: .env file not found!
    echo.
    echo Please copy .env.example to .env and configure it:
    echo   1. copy .env.example .env
    echo   2. Edit .env and configure at least one provider (FCM/Pushbullet/Ntfy)
    echo.
    pause
    exit /b 1
)

echo Starting notification forwarder...
echo Press Ctrl+C to stop
echo.

REM Run the application
python main.py

REM If the script exits, wait for user input
echo.
echo Application stopped.
pause
