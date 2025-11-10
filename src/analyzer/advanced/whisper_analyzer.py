"""
Whisper-based speech transcription
Requires: pip install -r requirements-medium.txt
"""
import numpy as np
from pathlib import Path
from typing import List, Dict, Optional
from moviepy.editor import VideoFileClip

from src.utils.config import Config
from src.utils.helpers import get_logger

logger = get_logger(__name__)

try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False
    logger.warning("Whisper not available. Install with: pip install -r requirements-medium.txt")


class WhisperAnalyzer:
    """
    Uses OpenAI's Whisper to transcribe speech in videos
    Can generate captions from spoken content
    """

    def __init__(self, model_name: str = None):
        """
        Initialize Whisper model

        Args:
            model_name: Model size (tiny, base, small, medium, large)
                       Default: base (~500MB)
        """
        if not WHISPER_AVAILABLE:
            raise ImportError("Whisper not installed. Run: pip install -r requirements-medium.txt")

        self.model_name = model_name or Config.WHISPER_MODEL

        logger.info(f"Loading Whisper model: {self.model_name}")
        logger.info("First load will download the model (may take a few minutes)")

        self.model = whisper.load_model(self.model_name)

        logger.info(f"✓ Whisper model loaded")

    def transcribe_video(self, video_path: Path,
                        language: str = None) -> Dict:
        """
        Transcribe speech in video

        Args:
            video_path: Path to video file
            language: Language code (e.g., 'en', 'es'). None for auto-detect

        Returns:
            Dictionary with transcription and segments
        """
        logger.info(f"Transcribing: {video_path}")

        # Extract audio from video
        audio_path = self._extract_audio(video_path)

        # Transcribe
        options = {}
        if language:
            options['language'] = language

        result = self.model.transcribe(str(audio_path), **options)

        # Clean up temp audio
        if audio_path.exists():
            audio_path.unlink()

        logger.info(f"✓ Transcribed {len(result['segments'])} segments")
        logger.info(f"Detected language: {result.get('language', 'unknown')}")

        return result

    def _extract_audio(self, video_path: Path) -> Path:
        """Extract audio from video to temporary file"""
        temp_audio = Config.get_temp_file(prefix="audio", suffix=".mp3")

        with VideoFileClip(str(video_path)) as video:
            if video.audio is None:
                logger.warning("Video has no audio track")
                # Create empty audio file
                temp_audio.touch()
            else:
                video.audio.write_audiofile(str(temp_audio), verbose=False, logger=None)

        return temp_audio

    def get_spoken_moments(self, video_path: Path,
                          min_duration: float = 1.0) -> List[Dict]:
        """
        Find moments when people are speaking

        Args:
            video_path: Path to video
            min_duration: Minimum speech duration to include

        Returns:
            List of speech segments with timing
        """
        result = self.transcribe_video(video_path)

        spoken_moments = []

        for segment in result['segments']:
            duration = segment['end'] - segment['start']

            if duration >= min_duration:
                spoken_moments.append({
                    'start': segment['start'],
                    'end': segment['end'],
                    'duration': duration,
                    'text': segment['text'].strip(),
                    'confidence': segment.get('avg_logprob', 0)
                })

        logger.info(f"✓ Found {len(spoken_moments)} spoken moments")
        return spoken_moments

    def generate_captions_from_speech(self, video_path: Path,
                                     max_words_per_caption: int = 5) -> List[Dict]:
        """
        Generate caption overlays from transcribed speech

        Args:
            video_path: Path to video
            max_words_per_caption: Maximum words per caption

        Returns:
            List of caption dictionaries
        """
        logger.info("Generating captions from speech")

        result = self.transcribe_video(video_path)

        captions = []

        for segment in result['segments']:
            text = segment['text'].strip()

            # Split long sentences into shorter captions
            words = text.split()

            if len(words) <= max_words_per_caption:
                # Short enough, use as-is
                captions.append({
                    'text': text,
                    'start_time': segment['start'],
                    'duration': segment['end'] - segment['start'],
                    'position': 'bottom'  # Typical for subtitles
                })
            else:
                # Split into multiple captions
                duration = segment['end'] - segment['start']
                words_per_second = len(words) / duration if duration > 0 else 1

                current_time = segment['start']
                for i in range(0, len(words), max_words_per_caption):
                    chunk = words[i:i + max_words_per_caption]
                    chunk_text = ' '.join(chunk)

                    chunk_duration = len(chunk) / words_per_second if words_per_second > 0 else 2

                    captions.append({
                        'text': chunk_text,
                        'start_time': current_time,
                        'duration': chunk_duration,
                        'position': 'bottom'
                    })

                    current_time += chunk_duration

        logger.info(f"✓ Generated {len(captions)} captions from speech")
        return captions

    def detect_language(self, video_path: Path) -> str:
        """
        Detect the language spoken in video

        Args:
            video_path: Path to video

        Returns:
            Language code (e.g., 'en', 'es', 'fr')
        """
        audio_path = self._extract_audio(video_path)

        # Load audio
        audio = whisper.load_audio(str(audio_path))

        # Detect language from first 30 seconds
        audio = whisper.pad_or_trim(audio)
        mel = whisper.log_mel_spectrogram(audio).to(self.model.device)

        _, probs = self.model.detect_language(mel)

        # Clean up
        if audio_path.exists():
            audio_path.unlink()

        detected_language = max(probs, key=probs.get)

        logger.info(f"✓ Detected language: {detected_language} ({probs[detected_language]:.2%})")

        return detected_language

    def find_keywords(self, video_path: Path,
                     keywords: List[str]) -> List[Dict]:
        """
        Find when specific keywords are mentioned in video

        Args:
            video_path: Path to video
            keywords: List of keywords to search for

        Returns:
            List of matches with timestamps
        """
        logger.info(f"Searching for keywords: {keywords}")

        result = self.transcribe_video(video_path)

        matches = []

        for segment in result['segments']:
            text = segment['text'].lower()

            for keyword in keywords:
                if keyword.lower() in text:
                    matches.append({
                        'keyword': keyword,
                        'timestamp': segment['start'],
                        'end': segment['end'],
                        'context': segment['text'].strip()
                    })

        logger.info(f"✓ Found {len(matches)} keyword matches")
        return matches

    def get_summary(self, video_path: Path,
                   max_sentences: int = 3) -> str:
        """
        Generate a brief summary of what's said in the video

        Args:
            video_path: Path to video
            max_sentences: Maximum sentences in summary

        Returns:
            Summary text
        """
        result = self.transcribe_video(video_path)

        full_text = result['text']

        # Simple summary: take first N sentences
        sentences = full_text.split('.')
        summary_sentences = sentences[:max_sentences]
        summary = '. '.join(s.strip() for s in summary_sentences if s.strip())

        if summary and not summary.endswith('.'):
            summary += '.'

        return summary

    @staticmethod
    def get_model_info() -> Dict:
        """Get information about available Whisper models"""
        return {
            'tiny': {'size': '~75MB', 'speed': 'Very Fast', 'accuracy': 'Low'},
            'base': {'size': '~150MB', 'speed': 'Fast', 'accuracy': 'Medium'},
            'small': {'size': '~500MB', 'speed': 'Medium', 'accuracy': 'Good'},
            'medium': {'size': '~1.5GB', 'speed': 'Slow', 'accuracy': 'Very Good'},
            'large': {'size': '~3GB', 'speed': 'Very Slow', 'accuracy': 'Best'}
        }
