@echo off
REM TeleCommand Pro Launcher for Windows
REM Starts both the bot and web portal

echo ======================================
echo   TeleCommand Pro - Starting Services
echo ======================================
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo [ERROR] Virtual environment not found!
    echo Please run setup.bat first
    pause
    exit /b 1
)

REM Check if config.json exists
if not exist "config.json" (
    echo [ERROR] config.json not found!
    echo Please create config.json from config.example.json
    pause
    exit /b 1
)

REM Start Web Portal in new window
echo [*] Starting Web Portal...
start "TeleCommand Pro Portal" cmd /c "venv\Scripts\activate.bat && python web_portal.py"
timeout /t 3 /nobreak >nul
echo [OK] Web Portal started

echo.

REM Start Bot in new window
echo [*] Starting TeleCommand Pro Bot...
start "TeleCommand Pro Bot" cmd /c "venv\Scripts\activate.bat && python bot.py"
timeout /t 2 /nobreak >nul
echo [OK] Bot started

echo.
echo ======================================
echo    All Services Running!
echo ======================================
echo.
echo Web Portal: http://localhost:5000
echo.
echo Bot: Running and waiting for commands
echo.
echo Contact administrator for login credentials
echo.
echo Two windows have been opened:
echo    1. TeleCommand Pro Portal
echo    2. TeleCommand Pro Bot
echo.
echo Close those windows to stop the services
echo.
pause
