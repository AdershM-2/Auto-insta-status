"""
Scene detection using OpenCV to identify cuts and scene changes in videos
"""
import cv2
import numpy as np
from pathlib import Path
from typing import List, Tuple
from moviepy.editor import VideoFileClip

from src.utils.config import Config
from src.utils.helpers import get_logger

logger = get_logger(__name__)


class SceneDetector:
    """
    Detects scene changes in videos using frame difference analysis
    """

    def __init__(self, threshold: float = None):
        """
        Args:
            threshold: Scene change detection threshold (0-100)
                      Higher = less sensitive
        """
        self.threshold = threshold or Config.SCENE_CHANGE_THRESHOLD

    def detect_scenes(self, video_path: Path) -> List[Tuple[float, float]]:
        """
        Detect scene changes in a video

        Args:
            video_path: Path to video file

        Returns:
            List of (start_time, end_time) tuples for each scene
        """
        logger.info(f"Detecting scenes in: {video_path}")

        cap = cv2.VideoCapture(str(video_path))
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        if fps == 0 or frame_count == 0:
            logger.error(f"Could not read video: {video_path}")
            return []

        scenes = []
        scene_start = 0
        prev_frame = None
        frame_idx = 0

        logger.info(f"Analyzing {frame_count} frames at {fps} fps")

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Convert to grayscale for comparison
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            if prev_frame is not None:
                # Calculate frame difference
                diff = cv2.absdiff(prev_frame, gray)
                diff_score = np.mean(diff)

                # If difference exceeds threshold, mark scene change
                if diff_score > self.threshold:
                    scene_end = frame_idx / fps
                    if scene_end - scene_start > Config.MIN_CLIP_DURATION:
                        scenes.append((scene_start, scene_end))
                        scene_start = scene_end
                        logger.debug(f"Scene change detected at {scene_end:.2f}s")

            prev_frame = gray
            frame_idx += 1

        # Add final scene
        final_time = frame_count / fps
        if final_time - scene_start > Config.MIN_CLIP_DURATION:
            scenes.append((scene_start, final_time))

        cap.release()

        logger.info(f"✓ Detected {len(scenes)} scenes")
        return scenes

    def get_best_scenes(self, video_path: Path, max_scenes: int = 5) -> List[Tuple[float, float]]:
        """
        Get the most interesting scenes from a video

        Args:
            video_path: Path to video file
            max_scenes: Maximum number of scenes to return

        Returns:
            List of best (start_time, end_time) tuples
        """
        scenes = self.detect_scenes(video_path)

        # Score each scene by motion/activity
        scored_scenes = []
        for start, end in scenes:
            score = self._score_scene(video_path, start, end)
            scored_scenes.append((score, start, end))

        # Sort by score and return top scenes
        scored_scenes.sort(reverse=True)
        best_scenes = [(start, end) for _, start, end in scored_scenes[:max_scenes]]

        return best_scenes

    def _score_scene(self, video_path: Path, start_time: float, end_time: float) -> float:
        """
        Score a scene based on motion and activity

        Returns:
            Score (higher = more interesting)
        """
        cap = cv2.VideoCapture(str(video_path))
        fps = cap.get(cv2.CAP_PROP_FPS)

        # Jump to start of scene
        start_frame = int(start_time * fps)
        end_frame = int(end_time * fps)
        cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

        motion_scores = []
        prev_frame = None

        for frame_idx in range(start_frame, end_frame, int(fps)):  # Sample at 1 fps
            ret, frame = cap.read()
            if not ret:
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            if prev_frame is not None:
                # Calculate motion
                diff = cv2.absdiff(prev_frame, gray)
                motion = np.mean(diff)
                motion_scores.append(motion)

            prev_frame = gray

        cap.release()

        # Return average motion as score
        return np.mean(motion_scores) if motion_scores else 0

    def find_best_moments(self, video_path: Path,
                         moment_duration: float = 3.0,
                         num_moments: int = 5) -> List[float]:
        """
        Find the best N-second moments in a video

        Args:
            video_path: Path to video file
            moment_duration: Duration of each moment in seconds
            num_moments: Number of moments to find

        Returns:
            List of start times for best moments
        """
        clip = VideoFileClip(str(video_path))
        duration = clip.duration
        clip.close()

        if duration < moment_duration:
            return [0]

        # Sample moments throughout the video
        cap = cv2.VideoCapture(str(video_path))
        fps = cap.get(cv2.CAP_PROP_FPS)

        moments = []
        step = max(1, int(fps))  # Sample at 1 fps

        for start_time in np.arange(0, duration - moment_duration, 1):
            score = self._score_moment(cap, fps, start_time, moment_duration)
            moments.append((score, start_time))

        cap.release()

        # Sort by score and return top moments
        moments.sort(reverse=True)
        best_moments = [start_time for _, start_time in moments[:num_moments]]

        return sorted(best_moments)  # Return in chronological order

    def _score_moment(self, cap: cv2.VideoCapture, fps: float,
                     start_time: float, duration: float) -> float:
        """Score a specific moment in the video"""
        start_frame = int(start_time * fps)
        end_frame = int((start_time + duration) * fps)

        cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

        scores = []
        prev_frame = None

        for _ in range(start_frame, end_frame, max(1, int(fps / 2))):
            ret, frame = cap.read()
            if not ret:
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Calculate sharpness (high = in focus)
            laplacian = cv2.Laplacian(gray, cv2.CV_64F)
            sharpness = laplacian.var()

            # Calculate motion
            motion = 0
            if prev_frame is not None:
                diff = cv2.absdiff(prev_frame, gray)
                motion = np.mean(diff)

            # Combined score
            score = sharpness + (motion * 10)
            scores.append(score)

            prev_frame = gray

        return np.mean(scores) if scores else 0
