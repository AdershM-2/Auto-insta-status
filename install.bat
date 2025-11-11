@echo off
REM Auto Instagram Status - Windows Requirements Installer
REM This script installs Python dependencies based on AI tier selection

echo ========================================
echo  Auto Instagram Status
echo  Requirements Installer
echo ========================================
echo.

REM Check Python
echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Please install Python 3.8+ from https://www.python.org/downloads/
    pause
    exit /b 1
)

python --version
echo [OK] Python found
echo.

REM Check if venv exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment
        pause
        exit /b 1
    )
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
python -m pip install --upgrade pip --quiet
echo [OK] pip upgraded
echo.

REM Ask user which tier to install
echo ========================================
echo  Select AI Model Tier
echo ========================================
echo.
echo Choose which AI models to install:
echo.
echo 1. Simple (Default)
echo    - Size: ~500MB
echo    - Models: MediaPipe, OpenCV, Librosa
echo    - Speed: Fast
echo    - Best for: Quick editing, testing
echo.
echo 2. Medium (Recommended)
echo    - Size: ~2.5GB
echo    - Models: Simple + CLIP + Whisper
echo    - Speed: Medium
echo    - Best for: Better scene understanding, speech transcription
echo.
echo 3. Advanced (Maximum Features)
echo    - Size: ~4GB
echo    - Models: Medium + YOLO + Emotion Detection
echo    - Speed: Slower but highest quality
echo    - Best for: Professional work, maximum quality
echo.
echo 4. Custom (Manual selection)
echo.

set /p tier="Enter choice (1-4) [1]: "
if "%tier%"=="" set tier=1

if "%tier%"=="1" goto simple
if "%tier%"=="2" goto medium
if "%tier%"=="3" goto advanced
if "%tier%"=="4" goto custom
goto invalid

:simple
echo.
echo ========================================
echo Installing Simple Tier (Core Dependencies)
echo ========================================
echo.
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Installation failed
    pause
    exit /b 1
)
goto success

:medium
echo.
echo ========================================
echo Installing Medium Tier (Core + CLIP + Whisper)
echo ========================================
echo.
echo This will download ~2.5GB of models...
echo.
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Installation failed
    pause
    exit /b 1
)
echo.
echo Installing medium tier models...
pip install -r requirements-medium.txt
if errorlevel 1 (
    echo [ERROR] Medium tier installation failed
    pause
    exit /b 1
)
goto success

:advanced
echo.
echo ========================================
echo Installing Advanced Tier (All Features)
echo ========================================
echo.
echo This will download ~4GB of models...
echo This may take 10-20 minutes depending on your internet speed.
echo.
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Installation failed
    pause
    exit /b 1
)
echo.
echo Installing advanced tier models...
pip install -r requirements-advanced.txt
if errorlevel 1 (
    echo [ERROR] Advanced tier installation failed
    pause
    exit /b 1
)
goto success

:custom
echo.
echo ========================================
echo Custom Installation
echo ========================================
echo.
echo Install core dependencies? (Required) (Y/n)
set /p core="Choice: "
if /i "%core%"=="n" goto skip_core
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Installation failed
    pause
    exit /b 1
)
:skip_core

echo.
echo Install CLIP + Whisper? (Medium tier) (y/N)
set /p medium_choice="Choice: "
if /i "%medium_choice%"=="y" (
    pip install -r requirements-medium.txt
    if errorlevel 1 (
        echo [ERROR] Medium tier installation failed
        pause
        exit /b 1
    )
)

echo.
echo Install YOLO + Emotion Detection? (Advanced tier) (y/N)
set /p advanced_choice="Choice: "
if /i "%advanced_choice%"=="y" (
    pip install -r requirements-advanced.txt
    if errorlevel 1 (
        echo [ERROR] Advanced tier installation failed
        pause
        exit /b 1
    )
)
goto success

:invalid
echo [ERROR] Invalid choice. Please run the script again.
pause
exit /b 1

:success
echo.
echo ========================================
echo  Testing Installation
echo ========================================
echo.

REM Test imports
python -c "import cv2, moviepy, librosa, mediapipe; print('[OK] Core libraries imported successfully')"
if errorlevel 1 (
    echo [ERROR] Some core libraries failed to import
    echo Try reinstalling: pip install -r requirements.txt --force-reinstall
    pause
    exit /b 1
)

REM Test advanced imports if installed
python -c "try: import open_clip; print('[OK] CLIP available')\nexcept: pass" 2>nul
python -c "try: import whisper; print('[OK] Whisper available')\nexcept: pass" 2>nul
python -c "try: import ultralytics; print('[OK] YOLO available')\nexcept: pass" 2>nul
python -c "try: import fer; print('[OK] Emotion Detection available')\nexcept: pass" 2>nul

echo.
echo ========================================
echo  Installation Complete!
echo ========================================
echo.
echo What you can do now:
echo.
echo 1. Check installed models:
echo    python main.py --show-models
echo.
echo 2. Create your first reel:
echo    python main.py --images "photo1.jpg,photo2.jpg" --description "My awesome day"
echo.
echo 3. See all options:
echo    python main.py --help
echo.
echo 4. (Optional) Install Ollama for local AI captions:
echo    Download from: https://ollama.ai/download
echo    Then run: ollama pull llama3.2
echo.
echo Need help? Check README.md or AI_MODELS.md
echo.
pause
