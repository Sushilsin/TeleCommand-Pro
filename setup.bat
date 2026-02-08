@echo off
REM Setup script for TeleCommand Pro on Windows

echo ================================
echo TeleCommand Pro - Setup
echo ================================
echo.

REM Check Python version
echo Checking Python version...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python 3.8 or higher.
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

python --version
echo [OK] Python found
echo.

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo [ERROR] Failed to create virtual environment
    pause
    exit /b 1
)
echo [OK] Virtual environment created
echo.

REM Activate virtual environment and install dependencies
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo [OK] Virtual environment activated
echo.

echo Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)
echo [OK] Dependencies installed
echo.

REM Create config from example if it doesn't exist
if not exist config.json (
    echo Creating config.json from example...
    copy config.example.json config.json
    echo [OK] config.json created
    echo.
    echo [IMPORTANT] Please edit config.json with:
    echo    1. Your Telegram bot token
    echo    2. Your Telegram user ID(s)
    echo.
) else (
    echo [WARNING] config.json already exists, skipping...
    echo.
)

echo ================================
echo Setup complete!
echo ================================
echo.
echo Next steps:
echo 1. Edit config.json with your bot token and user ID
echo 2. Run: venv\Scripts\activate.bat
echo 3. Run: python bot.py
echo.
echo For more information, see README.md
echo.
pause
