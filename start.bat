@echo off
setlocal

set "PROJECT_DIR=%~dp0"
cd /d "%PROJECT_DIR%"

echo ============================================
echo   HR Policy Q^&A Bot - Startup
echo ============================================
echo.

:: Check Python is installed and in PATH
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found in PATH.
    echo         Please install Python 3.8+ from https://www.python.org and try again.
    pause
    exit /b 1
)

echo [INFO] Python found:
python --version
echo.

:: Check .env file exists
if not exist "%PROJECT_DIR%.env" (
    echo [WARNING] No .env file found in project folder.
    echo           Copy .env.example to .env and add your GROQ_API_KEY before running.
    echo.
    echo           Example:
    echo             copy .env.example .env
    echo             Then open .env and set: GROQ_API_KEY=your_key_here
    echo.
    pause
    exit /b 1
)

echo [INFO] .env file found.
echo.

:: Check if venv exists
if exist "%PROJECT_DIR%venv\Scripts\activate.bat" (
    echo [INFO] Found existing virtual environment.
    goto :activate
)

:: venv not found — create it and install dependencies
echo [INFO] No virtual environment found. Creating one...
python -m venv venv

if errorlevel 1 (
    echo [ERROR] Failed to create virtual environment.
    echo         Make sure Python is installed correctly and try again.
    pause
    exit /b 1
)

echo [INFO] Virtual environment created. Installing dependencies...
call "%PROJECT_DIR%venv\Scripts\activate.bat"
pip install -r requirements.txt

if errorlevel 1 (
    echo [ERROR] Failed to install dependencies from requirements.txt.
    echo         Check your internet connection and try again.
    pause
    exit /b 1
)

echo.
echo [INFO] Dependencies installed successfully.
goto :run

:activate
echo [INFO] Activating virtual environment...
call "%PROJECT_DIR%venv\Scripts\activate.bat"
echo [INFO] Virtual environment activated.
echo.

:run
echo [INFO] Starting HR Policy Q^&A Bot...
echo [INFO] The app will open in your browser automatically.
echo [INFO] Press Ctrl+C in this window to stop the app.
echo.
streamlit run app.py

echo.
echo [INFO] App stopped.
pause
