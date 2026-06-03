@echo off
chcp 65001 >nul
echo.
echo ==========================================
echo   Raj -- Email Command Center
echo   Auto-send sequences ^| Draft-only replies
echo ==========================================
echo.

cd /d "%~dp0"

python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found in PATH
    echo Please install Python 3.10+ and check "Add to PATH"
    pause
    exit /b 1
)

echo [1/3] Checking packages...
python -c "import customtkinter, googleapiclient, openpyxl, requests" 2>nul
if errorlevel 1 (
    echo Installing missing packages...
    pip install -r requirements.txt
) else (
    echo [1/3] Packages ready
)

echo.
echo [2/3] Checking database...
python -c "from db import Database; d=Database(); print('[2/3] Database OK')"

echo.
echo [3/3] Starting Raj...
python main.py

echo.
pause
