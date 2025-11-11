# Quick Start Guide for Windows

Get Auto Instagram Status up and running in 5 minutes!

## Prerequisites

- **Python 3.8+** ([Download](https://www.python.org/downloads/))
  - ✅ Check "Add Python to PATH" during installation!
- **Git** ([Download](https://git-scm.com/download/win))
- **FFmpeg** (installer will guide you)

## Step-by-Step Installation

### 1. Clone the Repository

Open Command Prompt or PowerShell and run:

```cmd
git clone https://github.com/YOUR-USERNAME/Auto-insta-status.git
cd Auto-insta-status
```

### 2. Run the Installer

**Option A: Batch Script (Easiest)**
```cmd
install.bat
```

**Option B: PowerShell**
```powershell
.\install.ps1
```

The installer will:
1. ✅ Check your Python version
2. ✅ Create a virtual environment
3. ✅ Ask which AI tier you want
4. ✅ Install all dependencies
5. ✅ Test everything works

**Choose Your Tier:**
- **Simple** (500MB): Fast, good for most users ← Start here!
- **Medium** (2.5GB): Better quality, speech transcription
- **Advanced** (4GB): Maximum features

### 3. Install FFmpeg (Required)

If you don't have FFmpeg yet:

**Option 1: winget (Windows 10/11)**
```cmd
winget install ffmpeg
```

**Option 2: Chocolatey**
```cmd
choco install ffmpeg
```

**Option 3: Manual**
1. Download: https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip
2. Extract to `C:\ffmpeg`
3. Add `C:\ffmpeg\bin` to PATH (installer will remind you)

### 4. (Optional) Install Ollama for Free AI Captions

1. Download: https://ollama.ai/download
2. Install it
3. Open Command Prompt:
```cmd
ollama pull llama3.2
```

This gives you FREE local AI for caption generation!

## Your First Reel

### Activate Virtual Environment

Every time you use the tool, first activate:
```cmd
venv\Scripts\activate
```

You'll see `(venv)` appear in your prompt.

### Create a Reel

**Example 1: Simple images reel**
```cmd
python main.py --images "photo1.jpg,photo2.jpg,photo3.jpg" --description "My awesome vacation"
```

**Example 2: Images + Videos + Music**
```cmd
python main.py --images "IMG_*.jpg" --videos "VID_*.mp4" --music "song.mp3" --description "Epic beach adventure"
```

**Example 3: All files in a folder**
```cmd
python main.py --images "C:\Photos\Vacation\*.jpg" --description "Summer 2024"
```

The AI will:
1. 🔍 Analyze all your media
2. 🎬 Select the best moments
3. ✍️ Generate captions
4. 🎵 Sync to music beats
5. 📹 Create your reel!

Output will be in the `output` folder.

## Common Commands

### Check What AI Models You Have
```cmd
python main.py --show-models
```

### See All Options
```cmd
python main.py --help
```

### Upgrade to Better AI Models

Already installed simple tier? Upgrade:
```cmd
venv\Scripts\activate
pip install -r requirements-medium.txt     # Medium tier
pip install -r requirements-advanced.txt   # Advanced tier
```

### Create Longer/Shorter Reels
```cmd
# 15 second reel
python main.py --images "*.jpg" --description "Quick intro" --duration 15

# 60 second reel
python main.py --images "*.jpg" --videos "*.mp4" --description "Full story" --duration 60
```

### Different Styles
```cmd
python main.py --images "*.jpg" --description "Product launch" --style "professional"
```

Styles: `engaging`, `professional`, `fun`, `minimal`

## Folder Structure

```
Auto-insta-status/
├── venv/              # Virtual environment (created by installer)
├── output/            # Your finished reels go here
├── temp/              # Temporary files (auto-cleaned)
├── main.py            # Run this to create reels
├── install.bat        # Windows installer
└── requirements.txt   # Dependencies
```

## Tips for Best Results

### 1. **Use Good Quality Media**
- Images: At least 1080px
- Videos: 1080p or better

### 2. **Write Descriptive Text**
Bad: "beach"
Good: "Amazing sunset at the beach with friends laughing and having fun"

The AI uses your description to:
- Generate better captions
- Select relevant moments
- Create a story flow

### 3. **Music Matters**
- Use upbeat music for dynamic cuts
- Slow music = longer, calmer clips
- AI syncs cuts to the beat!

### 4. **File Paths**
- Use quotes for paths with spaces: `"C:\My Videos\clip.mp4"`
- Backslashes work: `"photos\vacation.jpg"`
- Forward slashes also work: `"photos/vacation.jpg"`
- Glob patterns: `"*.jpg"` finds all JPG files

## Troubleshooting

### "python is not recognized"
→ Python not in PATH. Reinstall Python and check "Add Python to PATH"

### "ffmpeg is not recognized"
→ FFmpeg not in PATH. Restart Command Prompt after installing FFmpeg

### "No module named 'cv2'"
→ Virtual environment not activated:
```cmd
venv\Scripts\activate
```

### "Permission denied"
→ Run Command Prompt as Administrator

### Slow processing
→ This is normal! Video editing is CPU-intensive.
- 30-second reel takes 2-5 minutes
- Upgrade to Medium/Advanced tier with GPU for faster processing

### Out of memory
→ Try:
- Closing other programs
- Using smaller videos
- Using Simple tier instead of Advanced

## Next Steps

### Upgrade Your AI Models

Start with Simple tier, then upgrade when you want:

**Medium Tier** (~2.5GB):
```cmd
pip install -r requirements-medium.txt
```
Adds:
- CLIP: Better scene understanding
- Whisper: Speech transcription

**Advanced Tier** (~4GB):
```cmd
pip install -r requirements-advanced.txt
```
Adds:
- YOLO: Object detection
- Emotion Detection: Find smiling moments

### Learn More

- **AI_MODELS.md** - Complete guide to all AI models
- **README.md** - Full documentation
- **WINDOWS_SETUP.md** - Detailed Windows guide

## Quick Reference

### Every time you start:
```cmd
cd Auto-insta-status
venv\Scripts\activate
```

### Create a reel:
```cmd
python main.py --images "*.jpg" --description "Your description"
```

### Check AI models:
```cmd
python main.py --show-models
```

### Get help:
```cmd
python main.py --help
```

---

**That's it! You're ready to create amazing AI-powered reels!** 🎬✨

Questions? Check README.md or open an issue on GitHub.
