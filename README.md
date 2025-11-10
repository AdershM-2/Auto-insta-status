# Auto Instagram Status - AI-Powered Reel Editor

A free, AI-powered tool that intelligently edits your images and videos into professional Instagram reels.

## Features

- 🤖 **AI Content Analysis**: Automatically detects best moments, faces, and interesting scenes
- ✂️ **Smart Clipping**: Intelligently snips videos at optimal points
- 📝 **Auto Captions**: Generates engaging text overlays based on your description
- 🎵 **Beat Sync**: Syncs cuts and transitions to music beats
- 🎨 **Smart Transitions**: Chooses appropriate transitions based on content
- 📐 **Auto-Framing**: Intelligently crops to 9:16 format while keeping subjects centered

## Installation

### Windows Users (Easiest Method)

**Option 1: Using Batch Script**
```cmd
setup.bat
```

**Option 2: Using PowerShell** (Run PowerShell as Administrator first)
```powershell
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
.\setup.ps1
```

### Linux/macOS Users

```bash
chmod +x setup.sh
./setup.sh
```

---

### Manual Installation (All Platforms)

#### 1. Install FFmpeg (Required)

**Windows:**
- **Option 1 (Easiest):** `winget install ffmpeg`
- **Option 2:** `choco install ffmpeg`
- **Option 3 (Manual):**
  1. Download from: https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip
  2. Extract to `C:\ffmpeg`
  3. Add `C:\ffmpeg\bin` to System PATH

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

#### 2. Install Python Dependencies

**Windows:**
```cmd
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

**Linux/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### 3. (Optional) Install Ollama for Local LLM

For AI caption generation without API costs:
- Download from: https://ollama.ai/download
- Install Ollama
- Pull the model:
```bash
ollama pull llama3.2
```

## Quick Start

**Windows:**
```cmd
python main.py --images "img1.jpg,img2.jpg,img3.jpg" --videos "clip1.mp4,clip2.mp4" --description "Amazing beach day with friends" --music "background.mp3" --output "output\my_reel.mp4"
```

**Linux/macOS:**
```bash
python main.py \
  --images "img1.jpg,img2.jpg,img3.jpg" \
  --videos "clip1.mp4,clip2.mp4" \
  --description "Amazing beach day with friends" \
  --music "background.mp3" \
  --output "output/my_reel.mp4"
```

## Project Structure

```
Auto-insta-status/
├── main.py                 # CLI entry point
├── src/
│   ├── analyzer/          # AI content analysis
│   │   ├── scene_detector.py
│   │   ├── face_detector.py
│   │   └── moment_scorer.py
│   ├── editor/            # Video editing logic
│   │   ├── video_processor.py
│   │   ├── clip_selector.py
│   │   └── transition_manager.py
│   ├── text/              # Text overlay & captions
│   │   ├── caption_generator.py
│   │   └── text_overlay.py
│   ├── audio/             # Music & beat detection
│   │   ├── beat_detector.py
│   │   └── audio_sync.py
│   └── utils/             # Helper functions
│       ├── config.py
│       └── helpers.py
└── output/                # Generated reels
```

## Usage Examples

### Basic Reel (Images Only)
```bash
python main.py --images "1.jpg,2.jpg,3.jpg" --description "My awesome day"
```

### With Videos and Music
**Windows:**
```cmd
python main.py --images "photo1.jpg,photo2.jpg" --videos "clip1.mp4,clip2.mp4" --music "song.mp3" --description "Epic adventure in the mountains"
```

**Linux/macOS:**
```bash
python main.py \
  --images "photo1.jpg,photo2.jpg" \
  --videos "clip1.mp4,clip2.mp4" \
  --music "song.mp3" \
  --description "Epic adventure in the mountains"
```

### Advanced Options
**Windows:**
```cmd
python main.py --images "photos\*.jpg" --videos "videos\*.mp4" --description "Product showcase" --duration 30 --music "background.mp3" --style "professional" --output "output\product_reel.mp4"
```

**Linux/macOS:**
```bash
python main.py \
  --images "photos/*.jpg" \
  --videos "videos/*.mp4" \
  --description "Product showcase" \
  --duration 30 \
  --music "background.mp3" \
  --style "professional" \
  --output "output/product_reel.mp4"
```

### Windows-Specific Tips
- Use quotes around paths with spaces: `"C:\My Videos\clip.mp4"`
- Use backslashes for paths: `"photos\vacation.jpg"`
- Or use forward slashes: `"photos/vacation.jpg"` (also works on Windows!)
- Glob patterns work: `"*.jpg"` will find all JPG files in current directory

## How It Works

1. **Analysis Phase**: AI scans all media to detect faces, objects, motion, and quality
2. **Planning Phase**: LLM generates story structure and caption plan based on description
3. **Selection Phase**: AI scores and selects best moments from videos/images
4. **Editing Phase**: Combines media with smart transitions, text, and music sync
5. **Render Phase**: Exports optimized 9:16 MP4 ready for Instagram

## Roadmap

- [x] Basic project structure
- [x] Core video processing engine
- [x] AI content analyzer (scene detection, face detection)
- [x] Smart clip selection
- [x] LLM caption generation (Ollama + OpenAI)
- [x] Beat detection & sync
- [x] Text overlay system
- [ ] GUI interface
- [ ] Web version
- [ ] Direct Instagram upload
- [ ] More AI effects (style transfer, filters)
- [ ] Batch processing

## License

MIT
