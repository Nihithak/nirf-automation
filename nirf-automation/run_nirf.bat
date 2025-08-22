@echo off
echo ========================================
echo    NIRF Automation System
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo Creating virtual environment...
    python -m venv venv
    echo Virtual environment created!
    echo.
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Ensure UTF-8 console to avoid Unicode/emoji issues on Windows
chcp 65001 > nul
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1

REM Install/update requirements
echo Installing/updating requirements...
pip install -r requirements.txt

echo.
echo ========================================
echo    Choose an option:
echo ========================================
echo 1. Run NIRF Analysis (Collect Data)
echo 2. Start Dashboard (View Results)
echo 3. Both (Analysis + Dashboard)
echo 4. Exit
echo ========================================
echo.

set /p choice="Enter your choice (1-4): "

if "%choice%"=="1" (
    echo.
    echo Starting NIRF Analysis...
    python main.py
    pause
) else if "%choice%"=="2" (
    echo.
    echo Starting Dashboard...
    echo Dashboard will be available at: http://localhost:5000
    echo Press Ctrl+C to stop the dashboard
    python dashboard/app.py
) else if "%choice%"=="3" (
    echo.
    echo Starting NIRF Analysis...
    start "NIRF Analysis" cmd /k "python main.py"
    echo.
    echo Waiting 5 seconds before starting dashboard...
    timeout /t 5 /nobreak >nul
    echo.
    echo Starting Dashboard...
    echo Dashboard will be available at: http://localhost:5000
    echo Press Ctrl+C to stop the dashboard
    python dashboard/app.py
) else if "%choice%"=="4" (
    echo Exiting...
    exit /b 0
) else (
    echo Invalid choice. Please run the script again.
    pause
    exit /b 1
)

pause

