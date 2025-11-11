# Auto Instagram Status - Windows Requirements Installer (PowerShell)
# This script installs Python dependencies based on AI tier selection

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Auto Instagram Status" -ForegroundColor Cyan
Write-Host " Requirements Installer" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check Python
Write-Host "Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python is not installed or not in PATH." -ForegroundColor Red
    Write-Host "Please install Python 3.8+ from https://www.python.org/downloads/" -ForegroundColor Red
    pause
    exit 1
}
Write-Host ""

# Check if venv exists
if (-not (Test-Path "venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "✗ Failed to create virtual environment" -ForegroundColor Red
        pause
        exit 1
    }
    Write-Host "✓ Virtual environment created" -ForegroundColor Green
} else {
    Write-Host "✓ Virtual environment already exists" -ForegroundColor Green
}
Write-Host ""

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& "venv\Scripts\Activate.ps1"
Write-Host ""

# Upgrade pip
Write-Host "Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip --quiet
Write-Host "✓ pip upgraded" -ForegroundColor Green
Write-Host ""

# Ask user which tier to install
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Select AI Model Tier" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Choose which AI models to install:" -ForegroundColor White
Write-Host ""

Write-Host "1. Simple (Default)" -ForegroundColor Yellow
Write-Host "   - Size: ~500MB" -ForegroundColor Gray
Write-Host "   - Models: MediaPipe, OpenCV, Librosa" -ForegroundColor Gray
Write-Host "   - Speed: Fast" -ForegroundColor Gray
Write-Host "   - Best for: Quick editing, testing" -ForegroundColor Gray
Write-Host ""

Write-Host "2. Medium (Recommended)" -ForegroundColor Yellow
Write-Host "   - Size: ~2.5GB" -ForegroundColor Gray
Write-Host "   - Models: Simple + CLIP + Whisper" -ForegroundColor Gray
Write-Host "   - Speed: Medium" -ForegroundColor Gray
Write-Host "   - Best for: Better scene understanding, speech transcription" -ForegroundColor Gray
Write-Host ""

Write-Host "3. Advanced (Maximum Features)" -ForegroundColor Yellow
Write-Host "   - Size: ~4GB" -ForegroundColor Gray
Write-Host "   - Models: Medium + YOLO + Emotion Detection" -ForegroundColor Gray
Write-Host "   - Speed: Slower but highest quality" -ForegroundColor Gray
Write-Host "   - Best for: Professional work, maximum quality" -ForegroundColor Gray
Write-Host ""

Write-Host "4. Custom (Manual selection)" -ForegroundColor Yellow
Write-Host ""

$tier = Read-Host "Enter choice (1-4) [1]"
if ([string]::IsNullOrWhiteSpace($tier)) {
    $tier = "1"
}

Write-Host ""

switch ($tier) {
    "1" {
        Write-Host "========================================" -ForegroundColor Cyan
        Write-Host "Installing Simple Tier (Core Dependencies)" -ForegroundColor Cyan
        Write-Host "========================================" -ForegroundColor Cyan
        Write-Host ""

        pip install -r requirements.txt
        if ($LASTEXITCODE -ne 0) {
            Write-Host "✗ Installation failed" -ForegroundColor Red
            pause
            exit 1
        }
    }

    "2" {
        Write-Host "========================================" -ForegroundColor Cyan
        Write-Host "Installing Medium Tier (Core + CLIP + Whisper)" -ForegroundColor Cyan
        Write-Host "========================================" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "This will download ~2.5GB of models..." -ForegroundColor Yellow
        Write-Host ""

        pip install -r requirements.txt
        if ($LASTEXITCODE -ne 0) {
            Write-Host "✗ Installation failed" -ForegroundColor Red
            pause
            exit 1
        }

        Write-Host ""
        Write-Host "Installing medium tier models..." -ForegroundColor Yellow
        pip install -r requirements-medium.txt
        if ($LASTEXITCODE -ne 0) {
            Write-Host "✗ Medium tier installation failed" -ForegroundColor Red
            pause
            exit 1
        }
    }

    "3" {
        Write-Host "========================================" -ForegroundColor Cyan
        Write-Host "Installing Advanced Tier (All Features)" -ForegroundColor Cyan
        Write-Host "========================================" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "This will download ~4GB of models..." -ForegroundColor Yellow
        Write-Host "This may take 10-20 minutes depending on your internet speed." -ForegroundColor Yellow
        Write-Host ""

        pip install -r requirements.txt
        if ($LASTEXITCODE -ne 0) {
            Write-Host "✗ Installation failed" -ForegroundColor Red
            pause
            exit 1
        }

        Write-Host ""
        Write-Host "Installing advanced tier models..." -ForegroundColor Yellow
        pip install -r requirements-advanced.txt
        if ($LASTEXITCODE -ne 0) {
            Write-Host "✗ Advanced tier installation failed" -ForegroundColor Red
            pause
            exit 1
        }
    }

    "4" {
        Write-Host "========================================" -ForegroundColor Cyan
        Write-Host "Custom Installation" -ForegroundColor Cyan
        Write-Host "========================================" -ForegroundColor Cyan
        Write-Host ""

        $core = Read-Host "Install core dependencies? (Required) (Y/n)"
        if ($core -ne "n" -and $core -ne "N") {
            pip install -r requirements.txt
            if ($LASTEXITCODE -ne 0) {
                Write-Host "✗ Installation failed" -ForegroundColor Red
                pause
                exit 1
            }
        }

        Write-Host ""
        $medium_choice = Read-Host "Install CLIP + Whisper? (Medium tier) (y/N)"
        if ($medium_choice -eq "y" -or $medium_choice -eq "Y") {
            pip install -r requirements-medium.txt
            if ($LASTEXITCODE -ne 0) {
                Write-Host "✗ Medium tier installation failed" -ForegroundColor Red
                pause
                exit 1
            }
        }

        Write-Host ""
        $advanced_choice = Read-Host "Install YOLO + Emotion Detection? (Advanced tier) (y/N)"
        if ($advanced_choice -eq "y" -or $advanced_choice -eq "Y") {
            pip install -r requirements-advanced.txt
            if ($LASTEXITCODE -ne 0) {
                Write-Host "✗ Advanced tier installation failed" -ForegroundColor Red
                pause
                exit 1
            }
        }
    }

    default {
        Write-Host "✗ Invalid choice. Please run the script again." -ForegroundColor Red
        pause
        exit 1
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Testing Installation" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Test imports
try {
    python -c "import cv2, moviepy, librosa, mediapipe; print('[OK] Core libraries imported successfully')"
    if ($LASTEXITCODE -ne 0) {
        throw "Import failed"
    }
} catch {
    Write-Host "✗ Some core libraries failed to import" -ForegroundColor Red
    Write-Host "Try reinstalling: pip install -r requirements.txt --force-reinstall" -ForegroundColor Yellow
    pause
    exit 1
}

# Test advanced imports if installed
python -c "try: import open_clip; print('[OK] CLIP available')`nexcept: pass" 2>$null
python -c "try: import whisper; print('[OK] Whisper available')`nexcept: pass" 2>$null
python -c "try: import ultralytics; print('[OK] YOLO available')`nexcept: pass" 2>$null
python -c "try: import fer; print('[OK] Emotion Detection available')`nexcept: pass" 2>$null

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host " Installation Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "What you can do now:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Check installed models:" -ForegroundColor White
Write-Host "   python main.py --show-models" -ForegroundColor Yellow
Write-Host ""
Write-Host "2. Create your first reel:" -ForegroundColor White
Write-Host '   python main.py --images "photo1.jpg,photo2.jpg" --description "My awesome day"' -ForegroundColor Yellow
Write-Host ""
Write-Host "3. See all options:" -ForegroundColor White
Write-Host "   python main.py --help" -ForegroundColor Yellow
Write-Host ""
Write-Host "4. (Optional) Install Ollama for local AI captions:" -ForegroundColor White
Write-Host "   Download from: https://ollama.ai/download" -ForegroundColor Yellow
Write-Host "   Then run: ollama pull llama3.2" -ForegroundColor Yellow
Write-Host ""
Write-Host "Need help? Check README.md or AI_MODELS.md" -ForegroundColor Gray
Write-Host ""
pause
