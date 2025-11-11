@echo off
REM Quick Reel Creator - Drag & Drop your folder here!

echo ========================================
echo  Quick Reel Creator
echo ========================================
echo.

REM Check if folder was provided
if "%~1"=="" (
    echo Error: No folder provided
    echo.
    echo Usage: Drag and drop your media folder onto this file
    echo Or run: quick-reel.bat "C:\path\to\folder"
    pause
    exit /b 1
)

set FOLDER=%~1

echo Media folder: %FOLDER%
echo.

REM Activate virtual environment
if not exist "venv\Scripts\activate.bat" (
    echo Error: Virtual environment not found
    echo Please run install.bat first
    pause
    exit /b 1
)

call venv\Scripts\activate.bat

REM Get description
echo What is this reel about?
echo Example: "Amazing beach vacation with friends"
echo.
set /p DESCRIPTION="Description: "

if "%DESCRIPTION%"=="" (
    echo Error: Description is required
    pause
    exit /b 1
)

echo.
echo Creating reel...
echo.

REM Run the tool
python main.py --folder "%FOLDER%" --description "%DESCRIPTION%"

echo.
pause
