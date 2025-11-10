#!/bin/bash
# Auto Instagram Status - Setup Script

set -e

echo "🚀 Auto Instagram Status Setup"
echo "================================"

# Check Python version
echo "Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d ' ' -f 2 | cut -d '.' -f 1,2)
echo "✓ Found Python $PYTHON_VERSION"

# Check FFmpeg
echo ""
echo "Checking FFmpeg..."
if ! command -v ffmpeg &> /dev/null; then
    echo "⚠️  FFmpeg is not installed."
    echo ""
    echo "Please install FFmpeg:"
    echo "  Ubuntu/Debian: sudo apt install ffmpeg"
    echo "  macOS:         brew install ffmpeg"
    echo "  Windows:       Download from https://ffmpeg.org/download.html"
    echo ""
    read -p "Continue without FFmpeg? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo "✓ FFmpeg is installed"
fi

# Create virtual environment
echo ""
echo "Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo ""
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo ""
echo "Creating directories..."
mkdir -p output temp

# Copy .env.example to .env if not exists
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "✓ Created .env file (edit this to configure API keys)"
fi

# Test installation
echo ""
echo "Testing installation..."
python3 -c "import cv2, moviepy, librosa, mediapipe; print('✓ All core libraries imported successfully')"

echo ""
echo "================================"
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Activate the virtual environment: source venv/bin/activate"
echo "2. (Optional) Install Ollama for local LLM: https://ollama.ai/download"
echo "3. (Optional) Run: ollama pull llama3.2"
echo "4. Run the tool: python main.py --help"
echo ""
echo "Example usage:"
echo "  python main.py --images 'photo1.jpg,photo2.jpg' --description 'My awesome day'"
echo ""
