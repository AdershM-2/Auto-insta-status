# Quick Reel Creator - PowerShell version
# Drag & Drop your folder here!

param(
    [Parameter(Mandatory=$false)]
    [string]$Folder
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Quick Reel Creator" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if folder was provided
if ([string]::IsNullOrWhiteSpace($Folder)) {
    Write-Host "Error: No folder provided" -ForegroundColor Red
    Write-Host ""
    Write-Host "Usage: Drag and drop your media folder onto this file" -ForegroundColor Yellow
    Write-Host "Or run: .\quick-reel.ps1 -Folder 'C:\path\to\folder'" -ForegroundColor Yellow
    pause
    exit 1
}

Write-Host "Media folder: $Folder" -ForegroundColor Green
Write-Host ""

# Activate virtual environment
if (-not (Test-Path "venv\Scripts\Activate.ps1")) {
    Write-Host "Error: Virtual environment not found" -ForegroundColor Red
    Write-Host "Please run install.bat or install.ps1 first" -ForegroundColor Yellow
    pause
    exit 1
}

& "venv\Scripts\Activate.ps1"

# Get description
Write-Host "What is this reel about?" -ForegroundColor Yellow
Write-Host "Example: 'Amazing beach vacation with friends'" -ForegroundColor Gray
Write-Host ""
$Description = Read-Host "Description"

if ([string]::IsNullOrWhiteSpace($Description)) {
    Write-Host "Error: Description is required" -ForegroundColor Red
    pause
    exit 1
}

Write-Host ""
Write-Host "Creating reel..." -ForegroundColor Yellow
Write-Host ""

# Run the tool
python main.py --folder "$Folder" --description "$Description"

Write-Host ""
pause
