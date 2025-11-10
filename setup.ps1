# Auto Instagram Status - Windows PowerShell Setup Script

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Auto Instagram Status - Windows Setup" -ForegroundColor Cyan
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
    Write-Host "Make sure to check 'Add Python to PATH' during installation!" -ForegroundColor Red
    pause
    exit 1
}
Write-Host ""

# Check FFmpeg
Write-Host "Checking FFmpeg..." -ForegroundColor Yellow
try {
    $null = ffmpeg -version 2>&1
    Write-Host "✓ FFmpeg is installed" -ForegroundColor Green
} catch {
    Write-Host "⚠ FFmpeg is not installed or not in PATH." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Please install FFmpeg:" -ForegroundColor Yellow
    Write-Host "  Option 1 (Recommended): winget install ffmpeg" -ForegroundColor White
    Write-Host "  Option 2: choco install ffmpeg" -ForegroundColor White
    Write-Host "  Option 3: Download from https://www.gyan.dev/ffmpeg/builds/" -ForegroundColor White
    Write-Host "           Extract to C:\ffmpeg and add C:\ffmpeg\bin to PATH" -ForegroundColor White
    Write-Host ""
    $continue = Read-Host "Continue without FFmpeg? (y/N)"
    if ($continue -ne "y" -and $continue -ne "Y") {
        exit 1
    }
}
Write-Host ""

# Create virtual environment
Write-Host "Creating virtual environment..." -ForegroundColor Yellow
if (-not (Test-Path "venv")) {
    python -m venv venv
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
python -m pip install --upgrade pip | Out-Null
Write-Host "✓ pip upgraded" -ForegroundColor Green
Write-Host ""

# Install dependencies
Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
Write-Host "This may take a few minutes..." -ForegroundColor Yellow
pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Failed to install dependencies" -ForegroundColor Red
    pause
    exit 1
}
Write-Host "✓ Dependencies installed" -ForegroundColor Green
Write-Host ""

# Create directories
Write-Host "Creating directories..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path "output" | Out-Null
New-Item -ItemType Directory -Force -Path "temp" | Out-Null
Write-Host "✓ Directories created" -ForegroundColor Green
Write-Host ""

# Create .env file
if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "✓ Created .env file" -ForegroundColor Green
}
Write-Host ""

# Test installation
Write-Host "Testing installation..." -ForegroundColor Yellow
python -c "import cv2, moviepy, librosa, mediapipe; print('✓ All core libraries imported successfully')"
if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Some libraries failed to import" -ForegroundColor Red
    pause
    exit 1
}
Write-Host ""

Write-Host "========================================" -ForegroundColor Green
Write-Host " Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Activate the virtual environment:" -ForegroundColor White
Write-Host "   venv\Scripts\Activate.ps1" -ForegroundColor Yellow
Write-Host ""
Write-Host "2. (Optional) Install Ollama for local AI captions:" -ForegroundColor White
Write-Host "   Download from: https://ollama.ai/download" -ForegroundColor Yellow
Write-Host "   Then run: ollama pull llama3.2" -ForegroundColor Yellow
Write-Host ""
Write-Host "3. Run the tool:" -ForegroundColor White
Write-Host "   python main.py --help" -ForegroundColor Yellow
Write-Host ""
Write-Host "Example usage:" -ForegroundColor Cyan
Write-Host '   python main.py --images "photo1.jpg,photo2.jpg" --description "My awesome day"' -ForegroundColor Yellow
Write-Host ""
pause
