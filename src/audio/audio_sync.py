"""
Synchronizes video cuts to music beats
"""
import numpy as np
from pathlib import Path
from typing import List, Dict
from dataclasses import dataclass

from src.utils.config import Config
from src.utils.helpers import get_logger
from .beat_detector import BeatDetector

logger = get_logger(__name__)


@dataclass
class SyncedClip:
    """Represents a clip synced to music"""
    clip_index: int
    start_time: float
    duration: float
    starts_on_beat: bool
    beat_timestamp: float = 0


class AudioSynchronizer:
    """
    Synchronizes video editing to music beats
    """

    def __init__(self):
        self.beat_detector = BeatDetector()

    def sync_clips_to_music(self,
                           clip_durations: List[float],
                           audio_path: Path,
                           target_duration: float) -> List[SyncedClip]:
        """
        Synchronize clip transitions to music beats

        Args:
            clip_durations: List of clip durations
            audio_path: Path to music file
            target_duration: Target total duration

        Returns:
            List of SyncedClip objects with adjusted timings
        """
        logger.info("Synchronizing clips to music beats")

        # Detect beats
        beat_times, tempo = self.beat_detector.detect_beats(audio_path)

        if len(beat_times) == 0:
            logger.warning("No beats detected, using original timings")
            return self._create_unsynced_clips(clip_durations)

        logger.info(f"Detected {len(beat_times)} beats at {tempo:.1f} BPM")

        # Assign clips to beats
        synced_clips = self._align_clips_to_beats(
            clip_durations,
            beat_times,
            target_duration
        )

        logger.info(f"✓ Synced {len(synced_clips)} clips to beats")

        return synced_clips

    def _create_unsynced_clips(self, clip_durations: List[float]) -> List[SyncedClip]:
        """Create clips without beat sync"""
        clips = []
        current_time = 0

        for i, duration in enumerate(clip_durations):
            clips.append(SyncedClip(
                clip_index=i,
                start_time=current_time,
                duration=duration,
                starts_on_beat=False
            ))
            current_time += duration

        return clips

    def _align_clips_to_beats(self,
                             clip_durations: List[float],
                             beat_times: np.ndarray,
                             target_duration: float) -> List[SyncedClip]:
        """
        Align clip start times to beats

        Strategy:
        1. Find beats that fit within target duration
        2. Assign clips to start on beats
        3. Adjust clip durations slightly to fit between beats
        """
        # Filter beats within target duration
        valid_beats = beat_times[beat_times < target_duration]

        if len(valid_beats) == 0:
            return self._create_unsynced_clips(clip_durations)

        num_clips = len(clip_durations)

        # Select beat indices for each clip
        if len(valid_beats) >= num_clips:
            # We have enough beats, select evenly
            beat_indices = np.linspace(0, len(valid_beats) - 1, num_clips).astype(int)
            selected_beats = valid_beats[beat_indices]
        else:
            # Not enough beats, some clips won't start on beats
            selected_beats = valid_beats
            # Add evenly spaced times for remaining clips
            remaining = num_clips - len(valid_beats)
            if remaining > 0:
                last_beat = valid_beats[-1]
                additional_times = np.linspace(
                    last_beat,
                    target_duration,
                    remaining + 2
                )[1:-1]
                selected_beats = np.concatenate([selected_beats, additional_times])

        # Create synced clips
        synced_clips = []

        for i in range(num_clips):
            start_time = selected_beats[i] if i < len(selected_beats) else target_duration

            # Calculate duration (to next beat or end)
            if i < num_clips - 1 and i + 1 < len(selected_beats):
                duration = selected_beats[i + 1] - start_time
            else:
                duration = target_duration - start_time

            # Don't exceed original duration too much
            original_duration = clip_durations[i]
            duration = min(duration, original_duration * 1.2)
            duration = max(duration, Config.MIN_CLIP_DURATION)

            is_on_beat = i < len(valid_beats)

            synced_clips.append(SyncedClip(
                clip_index=i,
                start_time=start_time,
                duration=duration,
                starts_on_beat=is_on_beat,
                beat_timestamp=start_time if is_on_beat else 0
            ))

        return synced_clips

    def suggest_transition_types(self,
                                audio_path: Path,
                                clip_transitions: List[float]) -> List[str]:
        """
        Suggest transition types based on music energy

        Args:
            audio_path: Path to music file
            clip_transitions: Timestamps of transitions

        Returns:
            List of transition types (fade, cut, zoom, etc.)
        """
        logger.info("Suggesting transitions based on music energy")

        # Get audio energy over time
        energy = self.beat_detector.get_audio_energy(audio_path)

        if len(energy) == 0:
            # Fallback: all fades
            return ['fade'] * len(clip_transitions)

        # Analyze music structure
        structure = self.beat_detector.analyze_music_structure(audio_path)
        avg_energy = structure.get('avg_energy', 0.5)

        transitions = []

        for transition_time in clip_transitions:
            # Get energy at this time
            # Map transition_time to energy array index
            duration = structure.get('duration', 30)
            index = int((transition_time / duration) * len(energy))
            index = min(index, len(energy) - 1)

            local_energy = energy[index] if index < len(energy) else avg_energy

            # Choose transition based on energy
            if local_energy > 0.7:
                # High energy: fast cut or zoom
                transitions.append('cut')
            elif local_energy > 0.4:
                # Medium energy: slide or fade
                transitions.append('fade')
            else:
                # Low energy: gentle fade
                transitions.append('fade')

        logger.info(f"✓ Suggested {len(transitions)} transitions")

        return transitions

    def adjust_pacing(self,
                     clip_durations: List[float],
                     audio_path: Path) -> List[float]:
        """
        Adjust clip pacing to match music energy

        Args:
            clip_durations: Original clip durations
            audio_path: Path to music file

        Returns:
            Adjusted clip durations
        """
        logger.info("Adjusting clip pacing to music energy")

        structure = self.beat_detector.analyze_music_structure(audio_path)

        if not structure:
            return clip_durations

        segments = structure.get('segments', [])

        if not segments:
            return clip_durations

        # Adjust durations based on music segments
        adjusted = clip_durations.copy()
        total_duration = sum(clip_durations)

        # Simple approach: faster cuts in high-energy sections
        for i, duration in enumerate(clip_durations):
            # Find which segment this clip is in
            clip_time = sum(clip_durations[:i])

            for segment in segments:
                if segment['start_time'] <= clip_time < segment['end_time']:
                    energy = segment['energy']

                    # High energy = shorter clips (faster pacing)
                    if energy > 0.7:
                        adjusted[i] = duration * 0.8
                    elif energy < 0.3:
                        adjusted[i] = duration * 1.2

                    break

        # Normalize to maintain total duration
        adjustment_factor = total_duration / sum(adjusted)
        adjusted = [d * adjustment_factor for d in adjusted]

        logger.info("✓ Adjusted clip pacing")

        return adjusted
