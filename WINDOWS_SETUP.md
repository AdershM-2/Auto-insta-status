# Windows Setup Guide

Complete setup guide for Windows users.

## Prerequisites

1. **Python 3.8 or higher**
   - Download from: https://www.python.org/downloads/
   - ✅ **IMPORTANT**: Check "Add Python to PATH" during installation!

2. **FFmpeg** (for video processing)
   - See installation options below

## Step 1: Install FFmpeg

Choose one of these methods:

### Option A: Using winget (Windows 10+, Easiest)
```cmd
winget install ffmpeg
```

### Option B: Using Chocolatey
```cmd
choco install ffmpeg
```

### Option C: Manual Installation
1. Download from: https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip
2. Extract to `C:\ffmpeg`
3. Add to PATH:
   - Press `Win + X` → System
   - Click "Advanced system settings"
   - Click "Environment Variables"
   - Under "System variables", find and select "Path"
   - Click "Edit" → "New"
   - Add: `C:\ffmpeg\bin`
   - Click OK on all windows
4. Open a NEW Command Prompt and test:
   ```cmd
   ffmpeg -version
   ```

## Step 2: Run Setup Script

### Using Batch File (Recommended)
1. Open Command Prompt in the project folder
2. Run:
   ```cmd
   setup.bat
   ```

### Using PowerShell
1. Open PowerShell **as Administrator**
2. Enable script execution:
   ```powershell
   Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```
3. Navigate to project folder and run:
   ```powershell
   .\setup.ps1
   ```

## Step 3: (Optional) Install Ollama for AI Captions

Ollama provides FREE local AI for generating captions without any API costs!

1. Download Ollama for Windows: https://ollama.ai/download
2. Install it
3. Open Command Prompt and run:
   ```cmd
   ollama pull llama3.2
   ```

This downloads a 2GB AI model that runs entirely on your PC.

## Step 4: Test Installation

1. Activate the virtual environment:
   ```cmd
   venv\Scripts\activate
   ```

2. Test the tool:
   ```cmd
   python main.py --help
   ```

You should see the help message with all available options.

## Creating Your First Reel

### Example 1: Simple Image Reel

```cmd
python main.py --images "photo1.jpg,photo2.jpg,photo3.jpg" --description "My awesome vacation"
```

### Example 2: With Videos and Music

```cmd
python main.py --images "IMG_001.jpg,IMG_002.jpg" --videos "VID_001.mp4,VID_002.mp4" --music "song.mp3" --description "Epic beach adventure with friends"
```

### Example 3: Using Glob Patterns

```cmd
REM All images in a folder
python main.py --images "C:\Photos\Vacation\*.jpg" --description "Summer 2024"

REM All videos from current folder
python main.py --videos "*.mp4" --description "My vlogs"

REM Mix of everything
python main.py --images "photos\*.jpg" --videos "videos\*.mp4" --music "music\background.mp3" --description "Product showcase reel" --duration 30
```

## Common Issues & Solutions

### Issue: "python is not recognized"
**Solution:** Python is not in PATH. Reinstall Python and check "Add Python to PATH"

### Issue: "ffmpeg is not recognized"
**Solution:** FFmpeg is not in PATH. Follow Step 1 again, make sure to restart Command Prompt after adding to PATH.

### Issue: "No module named 'cv2'" or similar
**Solution:** Virtual environment not activated or dependencies not installed.
```cmd
venv\Scripts\activate
pip install -r requirements.txt
```

### Issue: "Ollama connection failed"
**Solution:** Either Ollama is not installed or the service isn't running.
- Check if Ollama is installed
- Or use `--use-openai` flag if you have OpenAI API key

### Issue: "Permission denied" errors
**Solution:** Run Command Prompt as Administrator

### Issue: Slow video processing
**Solution:** This is normal! Video processing is CPU-intensive. A 30-second reel might take 2-5 minutes to create depending on your PC.

## Tips for Best Results

1. **Use High Quality Media**:
   - Images: At least 1080px on the shorter side
   - Videos: 1080p or higher

2. **Good Descriptions**:
   - Be specific: "Beach sunset with friends laughing" vs just "beach"
   - Mention mood: "energetic", "peaceful", "exciting"
   - AI uses this to generate better captions

3. **Music Selection**:
   - Use royalty-free music or music you have rights to
   - Upbeat music = faster cuts, slower music = longer clips
   - The AI syncs cuts to the music beats!

4. **File Paths**:
   - Use quotes for paths with spaces: `"C:\My Videos\clip.mp4"`
   - Forward slashes work too: `"C:/My Videos/clip.mp4"`
   - Relative paths: `"videos\clip.mp4"` (in current directory)

## Advanced Usage

### Custom Duration
```cmd
python main.py --images "*.jpg" --description "Quick intro" --duration 15
```

### Different Styles
```cmd
python main.py --images "*.jpg" --description "Product launch" --style "professional"
```

Available styles: `engaging`, `professional`, `fun`, `minimal`

### Custom Output Location
```cmd
python main.py --images "*.jpg" --description "My reel" --output "C:\Videos\output\my_reel.mp4"
```

### Disable Auto Captions
```cmd
python main.py --images "*.jpg" --description "Test" --no-captions
```

## Need Help?

- Check the main README.md for more details
- Open an issue on GitHub if you encounter problems
- Include your error message and Windows version

## System Requirements

**Minimum:**
- Windows 10 or 11
- Python 3.8+
- 4GB RAM
- 2GB free disk space

**Recommended:**
- Windows 11
- Python 3.11+
- 8GB RAM
- Dedicated GPU (for faster face detection)
- SSD for faster rendering

---

Enjoy creating amazing Instagram reels! 🎬✨
