@echo off
REM Auto Instagram Status - Windows Setup Script

echo ========================================
echo  Auto Instagram Status - Windows Setup
echo ========================================
echo.

REM Check Python
echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Please install Python 3.8 or higher from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation!
    pause
    exit /b 1
)

python --version
echo [OK] Python found
echo.

REM Check FFmpeg
echo Checking FFmpeg...
ffmpeg -version >nul 2>&1
if errorlevel 1 (
    echo [WARNING] FFmpeg is not installed or not in PATH.
    echo.
    echo Please install FFmpeg:
    echo 1. Download from: https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip
    echo 2. Extract to C:\ffmpeg
    echo 3. Add C:\ffmpeg\bin to your System PATH
    echo.
    echo Or install via Chocolatey: choco install ffmpeg
    echo Or install via winget: winget install ffmpeg
    echo.
    set /p continue="Continue without FFmpeg? (y/N): "
    if /i not "%continue%"=="y" exit /b 1
) else (
    echo [OK] FFmpeg is installed
)
echo.

REM Create virtual environment
echo Creating virtual environment...
if not exist "venv" (
    python -m venv venv
    echo [OK] Virtual environment created
) else (
    echo [OK] Virtual environment already exists
)
echo.

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo.

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip
echo.

REM Install dependencies
echo Installing Python dependencies...
echo This may take a few minutes...
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)
echo.

REM Create directories
echo Creating directories...
if not exist "output" mkdir output
if not exist "temp" mkdir temp
echo [OK] Directories created
echo.

REM Create .env file
if not exist ".env" (
    copy .env.example .env >nul
    echo [OK] Created .env file
)
echo.

REM Test installation
echo Testing installation...
python -c "import cv2, moviepy, librosa, mediapipe; print('[OK] All core libraries imported successfully')"
if errorlevel 1 (
    echo [ERROR] Some libraries failed to import
    pause
    exit /b 1
)
echo.

echo ========================================
echo  Setup Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Activate the virtual environment:
echo    venv\Scripts\activate
echo.
echo 2. (Optional) Install Ollama for local AI captions:
echo    Download from: https://ollama.ai/download
echo    Then run: ollama pull llama3.2
echo.
echo 3. Run the tool:
echo    python main.py --help
echo.
echo Example usage:
echo    python main.py --images "photo1.jpg,photo2.jpg" --description "My awesome day"
echo.
pause
