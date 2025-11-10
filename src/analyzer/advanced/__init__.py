"""
Advanced AI analyzers (requires medium/advanced tier models)
"""
from src.utils.config import Config

# Conditional imports based on available models
if Config.HAS_CLIP:
    from .clip_analyzer import CLIPAnalyzer
else:
    CLIPAnalyzer = None

if Config.HAS_WHISPER:
    from .whisper_analyzer import WhisperAnalyzer
else:
    WhisperAnalyzer = None

if Config.HAS_EMOTION_DETECTION:
    from .emotion_detector import EmotionDetector
else:
    EmotionDetector = None

if Config.HAS_YOLO:
    from .object_detector import ObjectDetector
else:
    ObjectDetector = None

__all__ = ['CLIPAnalyzer', 'WhisperAnalyzer', 'EmotionDetector', 'ObjectDetector']
