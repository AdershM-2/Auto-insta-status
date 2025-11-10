# Architecture Overview

## System Design

Auto Instagram Status is an AI-powered video editing pipeline that intelligently creates Instagram reels from raw media.

## Core Components

### 1. Video Processing Engine (`src/editor/`)

**VideoProcessor** (`video_processor.py`)
- Core video manipulation using MoviePy/FFmpeg
- Smart resizing and cropping to 9:16 format
- Clip concatenation and transitions
- Audio integration
- Final rendering

**ClipSelector** (`clip_selector.py`)
- Orchestrates clip selection using AI analysis
- Balances image and video content
- Adjusts durations to fit target length
- Orders clips for optimal flow

### 2. AI Analysis (`src/analyzer/`)

**SceneDetector** (`scene_detector.py`)
- Detects scene changes using frame difference
- Scores scenes by motion and activity
- Identifies best moments in videos
- Uses OpenCV for computer vision

**FaceDetector** (`face_detector.py`)
- Detects faces using MediaPipe
- Calculates smart crop regions
- Scores frames by face presence/quality
- Enables face-aware framing

**MomentScorer** (`moment_scorer.py`)
- Combines multiple analyses
- Scores video moments by:
  - Visual quality (sharpness, brightness, contrast)
  - Motion/activity level
  - Face presence and quality
- Removes overlapping clips
- Ranks and selects best moments

### 3. Text Generation (`src/text/`)

**CaptionGenerator** (`caption_generator.py`)
- Uses LLM (Ollama or OpenAI) for captions
- Generates engaging, contextual text
- Supports multiple styles
- Fallback generation when LLM unavailable

**TextOverlayManager** (`text_overlay.py`)
- Creates styled text clips
- Smart positioning (top/center/bottom)
- Fade animations
- Multiple style presets

### 4. Audio Processing (`src/audio/`)

**BeatDetector** (`beat_detector.py`)
- Detects music beats using Librosa
- Analyzes tempo and rhythm
- Identifies strong beats (downbeats)
- Calculates audio energy
- Segments music structure

**AudioSynchronizer** (`audio_sync.py`)
- Syncs video cuts to music beats
- Adjusts clip pacing to energy
- Suggests transition types
- Creates rhythmic editing

### 5. Utilities (`src/utils/`)

**Config** (`config.py`)
- Central configuration
- Video/audio settings
- AI parameters
- Path management

**Helpers** (`helpers.py`)
- File parsing and validation
- Logging setup
- Duration calculations
- Video metadata extraction

## Data Flow

```
1. INPUT
   ├── Images (JPG, PNG, etc.)
   ├── Videos (MP4, MOV, etc.)
   ├── Description (text)
   └── Music (optional MP3/WAV)

2. ANALYSIS PHASE
   ├── SceneDetector → Identify scenes
   ├── FaceDetector → Find faces
   └── MomentScorer → Score all moments

3. SELECTION PHASE
   ├── ClipSelector → Pick best clips
   └── AudioSync → Sync to beats (if music)

4. GENERATION PHASE
   ├── CaptionGenerator → Create text
   └── VideoProcessor → Load clips

5. COMPOSITION PHASE
   ├── TextOverlayManager → Add captions
   ├── VideoProcessor → Concatenate clips
   └── VideoProcessor → Add music

6. OUTPUT
   └── Final reel (MP4, 1080x1920, 30fps)
```

## AI Decision Making

### Clip Selection Algorithm

```python
For each video:
    1. Detect all scenes
    2. Score each scene:
       - Quality = sharpness + brightness + contrast
       - Motion = frame difference over time
       - Faces = presence + confidence + size
    3. Total = 0.3*quality + 0.3*motion + 0.4*faces
    4. Select top N non-overlapping moments

For each image:
    1. Score quality (sharpness, brightness, contrast)
    2. Detect and score faces
    3. Total = quality + faces
    4. Select top N images

Combine:
    1. Allocate ~60% time to videos, ~40% to images
    2. Adjust durations to fit target
    3. Order: Start strong, alternate types, end strong
```

### Caption Generation Flow

```
1. Build prompt with:
   - User description
   - Number of clips
   - Style preference
   - Timing requirements

2. Send to LLM (Ollama or OpenAI)

3. Parse JSON response:
   [
     {"text": "...", "clip_index": 0, "position": "top"},
     {"text": "...", "clip_index": 1, "position": "center"},
     ...
   ]

4. Map to absolute timings based on clip durations

5. Fallback if LLM unavailable:
   - Split description into phrases
   - Assign one per clip
   - Use simple positioning
```

### Beat Synchronization

```
1. Load audio with Librosa
2. Detect beats using onset detection
3. Extract strong beats (threshold filtering)
4. Map clips to beats:
   - Start each clip on nearest beat
   - Adjust duration to next beat
   - Maintain minimum/maximum clip lengths
5. Suggest transitions based on energy:
   - High energy (>0.7) → Fast cut
   - Medium (0.4-0.7) → Fade
   - Low (<0.4) → Gentle fade
```

## Performance Considerations

### Optimization Strategies

1. **Sampling**: Videos analyzed at reduced frame rates
   - Scene detection: Sample keyframes
   - Face detection: 1 fps sampling
   - Quality scoring: 0.5 fps sampling

2. **Parallel Processing**: Multiple clips loaded concurrently

3. **Smart Caching**: Face detections cached per timestamp

4. **Lazy Loading**: Clips loaded only when needed

5. **GPU Acceleration**: MediaPipe uses GPU when available

### Resource Usage

- **CPU**: Main bottleneck for video encoding
- **Memory**: ~500MB-2GB depending on clip count
- **Disk**: Temporary files in `temp/` directory
- **GPU**: Optional for MediaPipe acceleration

## Extensibility

### Adding New Features

1. **New Transitions**: Extend `VideoProcessor.apply_transition()`
2. **New Text Styles**: Add to `TextOverlayManager` style configs
3. **New AI Models**: Implement in `src/analyzer/`
4. **New Export Formats**: Extend `VideoProcessor.render()`

### Plugin Architecture (Future)

```python
class Plugin:
    def analyze(self, clip): pass
    def process(self, clip): pass
    def score(self, clip): pass
```

## Technology Stack

- **Video**: MoviePy, FFmpeg
- **Computer Vision**: OpenCV, MediaPipe
- **Object Detection**: YOLO (via Ultralytics)
- **Audio**: Librosa, PyDub
- **AI/LLM**: Ollama, OpenAI API
- **Image**: Pillow, NumPy
- **Python**: 3.8+

## Future Enhancements

1. **Web Interface**: Flask/FastAPI + React frontend
2. **Real-time Preview**: WebSocket streaming
3. **Cloud Processing**: AWS Lambda or similar
4. **More AI Models**: Style transfer, object removal
5. **Social Integration**: Direct upload to Instagram
6. **Template System**: Pre-made reel templates
7. **Batch Processing**: Process multiple reels
8. **Advanced Effects**: Filters, color grading, stabilization
