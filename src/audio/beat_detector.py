"""
Music beat detection using Librosa
"""
import numpy as np
from pathlib import Path
from typing import List, Tuple
import librosa

from src.utils.config import Config
from src.utils.helpers import get_logger

logger = get_logger(__name__)


class BeatDetector:
    """
    Detects beats in music for synchronized editing
    """

    def __init__(self):
        pass

    def detect_beats(self, audio_path: Path) -> Tuple[np.ndarray, float]:
        """
        Detect beat timestamps in audio file

        Args:
            audio_path: Path to audio file

        Returns:
            Tuple of (beat_times, tempo)
        """
        logger.info(f"Detecting beats in: {audio_path}")

        try:
            # Load audio
            y, sr = librosa.load(str(audio_path))

            # Detect tempo and beats
            tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)

            # Convert frames to time
            beat_times = librosa.frames_to_time(beat_frames, sr=sr)

            logger.info(f"✓ Detected {len(beat_times)} beats at {tempo:.1f} BPM")

            return beat_times, float(tempo)

        except Exception as e:
            logger.error(f"Error detecting beats: {e}")
            return np.array([]), 0.0

    def get_strong_beats(self, audio_path: Path, threshold: float = None) -> np.ndarray:
        """
        Get only strong/emphasized beats (downbeats)

        Args:
            audio_path: Path to audio file
            threshold: Strength threshold (0-1), None for auto

        Returns:
            Array of strong beat timestamps
        """
        if threshold is None:
            threshold = Config.BEAT_DETECTION_THRESHOLD

        logger.info(f"Detecting strong beats (threshold={threshold})")

        try:
            # Load audio
            y, sr = librosa.load(str(audio_path))

            # Onset strength
            onset_env = librosa.onset.onset_strength(y=y, sr=sr)

            # Detect beats
            tempo, beat_frames = librosa.beat.beat_track(
                onset_envelope=onset_env,
                sr=sr
            )

            # Get onset strength at each beat
            beat_strengths = onset_env[beat_frames]

            # Normalize strengths
            if len(beat_strengths) > 0:
                beat_strengths = beat_strengths / np.max(beat_strengths)

            # Filter strong beats
            strong_beat_frames = beat_frames[beat_strengths >= threshold]

            # Convert to time
            strong_beat_times = librosa.frames_to_time(strong_beat_frames, sr=sr)

            logger.info(f"✓ Found {len(strong_beat_times)} strong beats")

            return strong_beat_times

        except Exception as e:
            logger.error(f"Error detecting strong beats: {e}")
            return np.array([])

    def get_beat_intervals(self, beat_times: np.ndarray) -> List[Tuple[float, float]]:
        """
        Convert beat times to intervals between beats

        Args:
            beat_times: Array of beat timestamps

        Returns:
            List of (start, end) intervals
        """
        if len(beat_times) < 2:
            return []

        intervals = []
        for i in range(len(beat_times) - 1):
            intervals.append((beat_times[i], beat_times[i + 1]))

        return intervals

    def suggest_cut_points(self,
                          audio_path: Path,
                          num_cuts: int,
                          duration: float) -> List[float]:
        """
        Suggest optimal cut points synchronized to beats

        Args:
            audio_path: Path to audio file
            num_cuts: Number of cut points needed
            duration: Total duration to cover

        Returns:
            List of cut time points
        """
        logger.info(f"Suggesting {num_cuts} cut points for {duration:.1f}s")

        # Get beats
        beat_times, _ = self.detect_beats(audio_path)

        if len(beat_times) == 0:
            # Fallback: evenly spaced
            return list(np.linspace(0, duration, num_cuts + 2)[1:-1])

        # Filter beats within duration
        valid_beats = beat_times[beat_times <= duration]

        if len(valid_beats) <= num_cuts:
            return valid_beats.tolist()

        # Select evenly spaced beats
        indices = np.linspace(0, len(valid_beats) - 1, num_cuts).astype(int)
        selected_beats = valid_beats[indices]

        logger.info(f"✓ Selected {len(selected_beats)} beat-synced cut points")

        return selected_beats.tolist()

    def get_audio_energy(self, audio_path: Path, window_size: float = 0.5) -> np.ndarray:
        """
        Calculate audio energy over time

        Args:
            audio_path: Path to audio file
            window_size: Window size in seconds

        Returns:
            Array of energy values over time
        """
        try:
            # Load audio
            y, sr = librosa.load(str(audio_path))

            # Calculate RMS energy
            hop_length = int(sr * window_size)
            rms = librosa.feature.rms(y=y, hop_length=hop_length)[0]

            # Normalize
            rms = rms / np.max(rms) if np.max(rms) > 0 else rms

            return rms

        except Exception as e:
            logger.error(f"Error calculating audio energy: {e}")
            return np.array([])

    def analyze_music_structure(self, audio_path: Path) -> Dict:
        """
        Analyze music structure (intro, verse, chorus, etc.)

        Args:
            audio_path: Path to audio file

        Returns:
            Dictionary with structure information
        """
        logger.info(f"Analyzing music structure: {audio_path}")

        try:
            # Load audio
            y, sr = librosa.load(str(audio_path))

            # Get duration
            duration = librosa.get_duration(y=y, sr=sr)

            # Detect tempo
            tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)

            # Calculate energy
            rms = librosa.feature.rms(y=y)[0]
            avg_energy = np.mean(rms)
            energy_variance = np.var(rms)

            # Segment audio (simplified)
            # In a full implementation, would use librosa.segment.agglomerative
            segments = self._simple_segmentation(rms, sr)

            return {
                'duration': duration,
                'tempo': float(tempo),
                'avg_energy': float(avg_energy),
                'energy_variance': float(energy_variance),
                'segments': segments,
                'num_beats': len(beat_frames)
            }

        except Exception as e:
            logger.error(f"Error analyzing music: {e}")
            return {}

    def _simple_segmentation(self, rms: np.ndarray, sr: int) -> List[Dict]:
        """Simple energy-based segmentation"""
        # Divide into 4 segments (intro, build, peak, outro)
        segment_length = len(rms) // 4

        segments = []
        for i in range(4):
            start = i * segment_length
            end = (i + 1) * segment_length if i < 3 else len(rms)

            segment_rms = rms[start:end]
            avg_energy = np.mean(segment_rms)

            segment_names = ['intro', 'build', 'peak', 'outro']

            segments.append({
                'name': segment_names[i],
                'start_time': start * 512 / sr,  # Assuming default hop_length
                'end_time': end * 512 / sr,
                'energy': float(avg_energy)
            })

        return segments
