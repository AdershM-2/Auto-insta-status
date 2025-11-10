"""
Configuration management for Auto Instagram Status
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration settings for the reel editor"""

    # Project paths
    PROJECT_ROOT = Path(__file__).parent.parent.parent
    OUTPUT_DIR = PROJECT_ROOT / "output"
    TEMP_DIR = PROJECT_ROOT / "temp"

    # Video settings
    TARGET_WIDTH = 1080
    TARGET_HEIGHT = 1920  # 9:16 aspect ratio
    TARGET_FPS = 30
    DEFAULT_DURATION = 30  # seconds
    DEFAULT_IMAGE_DURATION = 3  # seconds per image

    # Quality settings
    VIDEO_CODEC = "libx264"
    AUDIO_CODEC = "aac"
    VIDEO_BITRATE = "8000k"
    AUDIO_BITRATE = "192k"

    # AI settings
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")

    # Analysis settings
    FACE_DETECTION_CONFIDENCE = 0.5
    SCENE_CHANGE_THRESHOLD = 30.0
    MIN_CLIP_DURATION = 2  # seconds
    MAX_CLIP_DURATION = 8  # seconds

    # Text overlay settings
    TEXT_FONT_SIZE = 60
    TEXT_POSITION = "center"  # top, center, bottom
    TEXT_DURATION = 3  # seconds
    TEXT_ANIMATION = "fade"  # fade, slide, zoom

    # Transition settings
    TRANSITION_DURATION = 0.5  # seconds
    AVAILABLE_TRANSITIONS = ["fade", "slide", "zoom", "wipe"]

    # Music settings
    MUSIC_FADE_IN = 1.0  # seconds
    MUSIC_FADE_OUT = 2.0  # seconds
    BEAT_DETECTION_THRESHOLD = 0.3

    @classmethod
    def ensure_dirs(cls):
        """Create necessary directories if they don't exist"""
        cls.OUTPUT_DIR.mkdir(exist_ok=True)
        cls.TEMP_DIR.mkdir(exist_ok=True)

    @classmethod
    def get_temp_file(cls, prefix="temp", suffix=".mp4"):
        """Generate a temporary file path"""
        cls.ensure_dirs()
        import uuid
        return cls.TEMP_DIR / f"{prefix}_{uuid.uuid4().hex[:8]}{suffix}"


# Initialize directories on import
Config.ensure_dirs()
