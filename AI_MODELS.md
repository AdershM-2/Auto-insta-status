# AI Models Guide

Complete guide to the AI models used in Auto Instagram Status reel editor.

## Model Tier System

The tool uses a **3-tier system** that lets you choose based on your hardware and needs:

| Tier | Models | Download Size | RAM Needed | Speed | Quality |
|------|--------|---------------|------------|-------|---------|
| **Simple** | Basic CV + LLM | ~500MB | 4GB | Fast | Good |
| **Medium** | + CLIP + Whisper | ~2.5GB | 8GB | Medium | Better |
| **Advanced** | + YOLO + Emotions | ~4GB | 12GB | Slower | Best |

## Installation

### Simple Tier (Default)
```bash
pip install -r requirements.txt
```

### Medium Tier
```bash
pip install -r requirements-medium.txt
```

### Advanced Tier
```bash
pip install -r requirements-advanced.txt
```

### Check Installed Models
```bash
python main.py --show-models
```

---

## Simple Tier (Always Available)

### 1. MediaPipe Face Detection
**What it does:** Detects faces in images and videos
**Use case:** Smart cropping, face-aware framing
**Speed:** Real-time (CPU)
**Model:** Google's lightweight CNN

**Features:**
- Detects multiple faces per frame
- Calculates confidence scores
- Provides bounding boxes
- Enables face-centered cropping

### 2. OpenCV Computer Vision
**What it does:** Traditional computer vision analysis
**Use case:** Scene detection, quality assessment
**Speed:** Very fast (CPU)

**Features:**
- Scene change detection (frame differencing)
- Quality scoring (sharpness, brightness, contrast)
- Motion analysis
- No deep learning required

### 3. Librosa Audio Analysis
**What it does:** Music and audio processing
**Use case:** Beat detection, tempo analysis
**Speed:** Fast (CPU)

**Features:**
- Beat detection and tracking
- Tempo estimation
- Onset detection
- Audio energy analysis
- Music structure segmentation

### 4. Llama 3.2 via Ollama
**What it does:** Text generation for captions
**Use case:** Creating engaging captions
**Speed:** Medium (CPU/GPU)
**Model:** 2B parameter LLM

**Features:**
- Runs completely locally (free!)
- Generates contextual captions
- Multiple style support
- Falls back to simple generation if unavailable

---

## Medium Tier (Enhanced Understanding)

### 5. CLIP (Contrastive Language-Image Pre-training)
**What it does:** Understands images semantically
**Use case:** Find specific scenes, rank by relevance
**Speed:** Medium (GPU recommended)
**Model:** OpenAI's vision-language model
**Size:** ~350MB (ViT-B/32)

**Features:**
- Search for scenes by text ("find beach scenes")
- Rank images by relevance to description
- Classify scene categories
- Understand content beyond objects
- No training needed - zero-shot learning

**Example Usage:**
```python
from src.analyzer.advanced import CLIPAnalyzer

# Initialize
clip = CLIPAnalyzer()

# Find matching frames
matches = clip.find_matching_frames(
    video_path="vacation.mp4",
    query="beautiful sunset at the beach",
    threshold=0.3
)

# Rank images
ranked = clip.rank_images_by_query(
    image_paths=["img1.jpg", "img2.jpg"],
    query="people smiling and laughing"
)
```

### 6. Whisper (Speech Recognition)
**What it does:** Transcribes speech in videos
**Use case:** Auto-generate captions from dialogue
**Speed:** Medium (GPU recommended)
**Model:** OpenAI's multilingual speech recognition
**Size:** ~150MB (base), up to 3GB (large)

**Available Models:**
- `tiny`: 75MB, very fast, low accuracy
- `base`: 150MB, fast, medium accuracy ✅ Default
- `small`: 500MB, medium, good accuracy
- `medium`: 1.5GB, slow, very good
- `large`: 3GB, very slow, best accuracy

**Features:**
- Multilingual support (90+ languages)
- Automatic language detection
- Timestamp-accurate transcription
- Find when keywords are mentioned
- Generate subtitles automatically

**Example Usage:**
```python
from src.analyzer.advanced import WhisperAnalyzer

# Initialize
whisper = WhisperAnalyzer(model_name="base")

# Transcribe video
result = whisper.transcribe_video("speech.mp4")

# Generate captions from speech
captions = whisper.generate_captions_from_speech(
    "interview.mp4",
    max_words_per_caption=5
)

# Find keywords
matches = whisper.find_keywords(
    "vlog.mp4",
    keywords=["amazing", "incredible", "wow"]
)
```

---

## Advanced Tier (Maximum Features)

### 7. YOLO v8 (Object Detection)
**What it does:** Detects 80+ object types
**Use case:** Find specific objects, track subjects
**Speed:** Medium-Fast (GPU recommended)
**Model:** Ultralytics YOLOv8
**Size:** 6MB (nano) to 130MB (xlarge)

**Model Sizes:**
- `n` (nano): Fastest, good for CPU ✅ Default
- `s` (small): Fast, better accuracy
- `m` (medium): Balanced
- `l` (large): Slower, high accuracy
- `x` (xlarge): Slowest, best accuracy

**Detectable Objects:** (80 classes)
- People, animals (dog, cat, horse, etc.)
- Vehicles (car, bicycle, motorcycle, etc.)
- Sports equipment (ball, racket, skateboard, etc.)
- Food items (pizza, banana, apple, etc.)
- Furniture and electronics

**Features:**
- Count people in videos
- Find specific objects
- Detect action shots (sports equipment)
- Smart focus point calculation
- Content richness scoring

**Example Usage:**
```python
from src.analyzer.advanced import ObjectDetector

# Initialize
yolo = ObjectDetector(model_size='n')  # nano model

# Count people
stats = yolo.count_people_in_video("party.mp4")
print(f"Average people: {stats['average']}")

# Find objects
appearances = yolo.find_object_appearances(
    "vacation.mp4",
    object_names=['dog', 'surfboard', 'car']
)

# Find action shots
action_shots = yolo.find_action_shots("sports.mp4")
```

### 8. FER (Facial Expression Recognition)
**What it does:** Detects emotions in faces
**Use case:** Find happy moments, emotional scenes
**Speed:** Medium (GPU recommended)
**Model:** Deep CNN for emotion classification
**Size:** ~100MB

**Detected Emotions:**
- Happy 😊
- Sad 😢
- Angry 😠
- Surprise 😲
- Fear 😨
- Disgust 🤢
- Neutral 😐

**Features:**
- Analyze emotions throughout video
- Find happy/smiling moments
- Search for specific emotions
- Calculate positivity scores
- Determine overall mood

**Example Usage:**
```python
from src.analyzer.advanced import EmotionDetector

# Initialize
emotion = EmotionDetector()

# Find happy moments
happy_moments = emotion.find_happy_moments(
    "birthday.mp4",
    threshold=0.5,  # 50% happiness
    min_duration=2.0  # at least 2 seconds
)

# Analyze overall emotions
analysis = emotion.analyze_video_emotions("video.mp4")
print(f"Most common: {analysis['most_common']}")

# Get statistics
stats = emotion.get_emotion_statistics("family.mp4")
print(f"Mood: {stats['mood']}")
print(f"Average happiness: {stats['average_happiness']:.1f}%")
```

---

## How AI Models Work Together

### Scene Selection Pipeline

```
1. Basic Analysis (Simple Tier)
   ├─ OpenCV: Detect scenes, measure quality
   ├─ MediaPipe: Find faces
   └─ Score: Quality (30%) + Motion (30%) + Faces (40%)

2. Enhanced Analysis (Medium Tier)
   ├─ CLIP: Understand scene semantics
   ├─ "Find beach scenes" → Ranks all scenes
   ├─ Whisper: Transcribe speech
   └─ Uses spoken content for better selection

3. Advanced Analysis (Advanced Tier)
   ├─ YOLO: Detect objects and people
   ├─ Emotion: Find moments with smiles
   └─ Combined scoring for best results
```

### Caption Generation Pipeline

```
Simple Tier:
User description → Llama 3.2 → Generated captions

Medium Tier:
User description + CLIP scene understanding → Better captions
User description + Whisper transcription → Speech-based captions

Advanced Tier:
All of the above + detected emotions → Contextual captions
```

---

## Performance Comparison

### Processing Time (30-second reel)

| Operation | Simple | Medium | Advanced |
|-----------|--------|--------|----------|
| Scene Analysis | 10s | 25s | 45s |
| Caption Generation | 5s | 8s | 10s |
| Total Processing | ~30s | ~60s | ~90s |

*Times on: Intel i5, 8GB RAM, no GPU*

### Quality Comparison

| Aspect | Simple | Medium | Advanced |
|--------|--------|--------|----------|
| Scene Selection | Good | Better | Best |
| Text Relevance | Good | Very Good | Excellent |
| Timing Accuracy | Good | Good | Excellent |
| Overall Polish | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

---

## Hardware Requirements

### Minimum (Simple Tier)
- CPU: Dual-core, 2GHz+
- RAM: 4GB
- Disk: 2GB free
- GPU: Not required

### Recommended (Medium Tier)
- CPU: Quad-core, 2.5GHz+
- RAM: 8GB
- Disk: 5GB free
- GPU: 4GB VRAM (optional but faster)

### Optimal (Advanced Tier)
- CPU: 6+ cores, 3GHz+
- RAM: 16GB
- Disk: 10GB free
- GPU: 6GB+ VRAM (highly recommended)

---

## Tips for Best Results

### 1. Start Simple
Begin with the simple tier. Most users find it sufficient for great results.

### 2. Upgrade Gradually
Try medium tier if you need:
- Better scene understanding
- Speech transcription
- More contextual captions

### 3. Use Advanced for Professional Work
Advanced tier is best for:
- Maximum quality
- Specific object detection needs
- Emotion-based editing
- Commercial projects

### 4. GPU Acceleration
If you have a GPU:
- PyTorch will use it automatically
- 3-5x speed improvement
- Much better experience

### 5. Model Selection
**For Whisper:**
- Use `tiny` for quick tests
- Use `base` for general use (default)
- Use `small/medium` for important videos

**For YOLO:**
- Use `n` (nano) for CPU
- Use `s` (small) for GPU
- Use `m/l` only if needed

---

## Frequently Asked Questions

### Q: Do I need internet for these models?
**A:** Only for the first download. After that, everything runs locally.

### Q: Can I use without GPU?
**A:** Yes! Simple tier works great on CPU. Medium/Advanced are slower but work.

### Q: How much does it cost?
**A:** $0. All models are completely free and open-source.

### Q: Which tier should I use?
**A:**
- **Casual use:** Simple
- **Better quality:** Medium
- **Professional:** Advanced

### Q: Can I mix tiers?
**A:** Yes! Install what you want. The tool auto-detects available models.

### Q: Do models improve over time?
**A:** Yes! We'll update to newer versions as they're released.

---

## Troubleshooting

### "CLIP not available"
```bash
pip install -r requirements-medium.txt
```

### "Out of memory" errors
- Use smaller models (Whisper: tiny, YOLO: nano)
- Close other applications
- Process shorter videos
- Upgrade RAM

### Slow processing
- Use GPU if available
- Choose smaller models
- Reduce video resolution
- Use simple tier

### Models not detected
```bash
python main.py --show-models
```
Check which models are installed.

---

## Future Models (Roadmap)

- **Depth Estimation** (MiDaS): 3D effects
- **Style Transfer**: Artistic effects
- **Audio Separation** (Demucs): Smart audio mixing
- **Music Generation**: Custom soundtracks
- **GPT-4 Vision**: Next-level understanding

---

## Credits

- **CLIP**: OpenAI
- **Whisper**: OpenAI
- **YOLO**: Ultralytics
- **MediaPipe**: Google
- **FER**: Justin Shenk
- **Librosa**: librosa development team
- **Llama**: Meta AI

All models are open-source and free to use! 🎉
