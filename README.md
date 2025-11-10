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

### 1. Install FFmpeg (Required)

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**Windows:**
Download from https://ffmpeg.org/download.html and add to PATH

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 3. (Optional) Install Ollama for Local LLM

For AI caption generation without API costs:
```bash
# Visit https://ollama.ai/download
# Then pull Llama model:
ollama pull llama3.2
```

## Quick Start

```bash
python main.py \
  --images "img1.jpg,img2.jpg,img3.jpg" \
  --videos "clip1.mp4,clip2.mp4" \
  --description "Amazing beach day with friends" \
  --music "background.mp3" \
  --output "my_reel.mp4"
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
```bash
python main.py \
  --images "photo1.jpg,photo2.jpg" \
  --videos "clip1.mp4,clip2.mp4" \
  --music "song.mp3" \
  --description "Epic adventure in the mountains"
```

### Advanced Options
```bash
python main.py \
  --images "*.jpg" \
  --videos "*.mp4" \
  --description "Product showcase" \
  --duration 30 \
  --music "background.mp3" \
  --style "dynamic" \
  --text-style "modern" \
  --output "product_reel.mp4"
```

## How It Works

1. **Analysis Phase**: AI scans all media to detect faces, objects, motion, and quality
2. **Planning Phase**: LLM generates story structure and caption plan based on description
3. **Selection Phase**: AI scores and selects best moments from videos/images
4. **Editing Phase**: Combines media with smart transitions, text, and music sync
5. **Render Phase**: Exports optimized 9:16 MP4 ready for Instagram

## Roadmap

- [x] Basic project structure
- [ ] Core video processing engine
- [ ] AI content analyzer
- [ ] Smart clip selection
- [ ] LLM caption generation
- [ ] Beat detection & sync
- [ ] Text overlay system
- [ ] GUI interface
- [ ] Web version

## License

MIT
