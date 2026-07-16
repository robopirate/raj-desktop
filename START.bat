@echo off
chcp 65001 >nul
echo.
echo ==========================================
echo   Raj -- Email Command Center
echo   Auto-send sequences ^| Draft-only replies
echo ==========================================
echo.

cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo [1/3] Creating virtual environment...
    python -m venv .venv
    if errorlevel 1 (
        echo ERROR: Could not create virtual environment.
        pause
        exit /b 1
    )
)

echo [1/3] Checking packages...
.venv\Scripts\python -c "import flask, pywebview, pystray, plyer" 2>nul
if errorlevel 1 (
    echo Installing / updating packages...
    .venv\Scripts\pip install -r requirements.txt
) else (
    echo [1/3] Packages ready
)

echo.
echo [2/3] Checking database...
.venv\Scripts\python -c "from db import Database; d=Database(); print('[2/3] Database OK')"

echo.
echo [3/3] Starting Raj Desktop...
.venv\Scripts\python desktop.py

echo.
pause
