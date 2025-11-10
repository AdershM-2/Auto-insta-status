"""
Intelligent moment scoring combining multiple AI analyses
"""
import cv2
import numpy as np
from pathlib import Path
from typing import List, Dict, Tuple
from dataclasses import dataclass

from src.utils.config import Config
from src.utils.helpers import get_logger
from .scene_detector import SceneDetector
from .face_detector import FaceDetector

logger = get_logger(__name__)


@dataclass
class MomentScore:
    """Data class for moment scoring results"""
    start_time: float
    end_time: float
    total_score: float
    quality_score: float
    motion_score: float
    face_score: float
    has_faces: bool
    num_faces: int


class MomentScorer:
    """
    Combines multiple AI analyses to intelligently score video moments
    """

    def __init__(self):
        self.scene_detector = SceneDetector()
        self.face_detector = FaceDetector()

    def score_video(self, video_path: Path,
                   num_clips: int = 5,
                   clip_duration: float = None) -> List[MomentScore]:
        """
        Analyze entire video and return best moments

        Args:
            video_path: Path to video file
            num_clips: Number of best clips to return
            clip_duration: Desired duration of each clip (None = auto)

        Returns:
            List of MomentScore objects, sorted by total_score
        """
        logger.info(f"Scoring moments in: {video_path}")

        if clip_duration is None:
            clip_duration = Config.MIN_CLIP_DURATION

        # Get video info
        cap = cv2.VideoCapture(str(video_path))
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = frame_count / fps
        cap.release()

        # Detect scenes first
        scenes = self.scene_detector.detect_scenes(video_path)
        logger.info(f"Found {len(scenes)} scenes")

        # Detect faces
        face_detections = self.face_detector.detect_faces_in_video(
            video_path,
            sample_rate=int(fps)  # Sample every second
        )

        # Score each potential clip
        scored_moments = []

        # Sample potential clip start times
        step = max(1.0, clip_duration / 2)  # 50% overlap
        for start_time in np.arange(0, duration - clip_duration, step):
            end_time = min(start_time + clip_duration, duration)

            # Calculate scores
            quality = self._score_quality(video_path, start_time, end_time)
            motion = self._score_motion(video_path, start_time, end_time)
            face_score, num_faces, has_faces = self._score_faces(
                face_detections, start_time, end_time
            )

            # Weight the scores
            # Quality: 30%, Motion: 30%, Faces: 40%
            total_score = (quality * 0.3) + (motion * 0.3) + (face_score * 0.4)

            moment = MomentScore(
                start_time=start_time,
                end_time=end_time,
                total_score=total_score,
                quality_score=quality,
                motion_score=motion,
                face_score=face_score,
                has_faces=has_faces,
                num_faces=num_faces
            )

            scored_moments.append(moment)

        # Sort by total score
        scored_moments.sort(key=lambda m: m.total_score, reverse=True)

        # Remove overlapping clips, keep highest scoring
        final_moments = self._remove_overlaps(scored_moments[:num_clips * 3], clip_duration)

        logger.info(f"✓ Selected {len(final_moments[:num_clips])} best moments")
        return final_moments[:num_clips]

    def _score_quality(self, video_path: Path,
                      start_time: float, end_time: float) -> float:
        """
        Score clip quality (sharpness, brightness, contrast)

        Returns:
            Score 0-100
        """
        cap = cv2.VideoCapture(str(video_path))
        fps = cap.get(cv2.CAP_PROP_FPS)

        start_frame = int(start_time * fps)
        end_frame = int(end_time * fps)

        cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

        quality_scores = []

        # Sample frames in the clip
        sample_rate = max(1, int(fps / 2))  # Sample at 0.5 fps
        for frame_idx in range(start_frame, end_frame, sample_rate):
            ret, frame = cap.read()
            if not ret:
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Sharpness (Laplacian variance)
            laplacian = cv2.Laplacian(gray, cv2.CV_64F)
            sharpness = laplacian.var()

            # Brightness
            brightness = np.mean(gray)

            # Contrast (standard deviation)
            contrast = np.std(gray)

            # Combined quality score
            # Good sharpness > 100, good brightness = 100-150, good contrast > 50
            quality = (
                min(sharpness / 10, 100) * 0.4 +  # Sharpness weight
                min(abs(brightness - 128) / 1.28, 100) * 0.3 +  # Brightness (prefer mid-range)
                min(contrast / 0.5, 100) * 0.3  # Contrast weight
            )

            quality_scores.append(quality)

        cap.release()

        return np.mean(quality_scores) if quality_scores else 0

    def _score_motion(self, video_path: Path,
                     start_time: float, end_time: float) -> float:
        """
        Score motion/activity in clip

        Returns:
            Score 0-100
        """
        cap = cv2.VideoCapture(str(video_path))
        fps = cap.get(cv2.CAP_PROP_FPS)

        start_frame = int(start_time * fps)
        end_frame = int(end_time * fps)

        cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

        motion_scores = []
        prev_frame = None

        sample_rate = max(1, int(fps / 4))  # Sample at 4 fps
        for frame_idx in range(start_frame, end_frame, sample_rate):
            ret, frame = cap.read()
            if not ret:
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            if prev_frame is not None:
                # Frame difference
                diff = cv2.absdiff(prev_frame, gray)
                motion = np.mean(diff)
                motion_scores.append(motion)

            prev_frame = gray

        cap.release()

        if not motion_scores:
            return 0

        # Normalize motion score (typical good motion is 5-30)
        avg_motion = np.mean(motion_scores)
        normalized = min((avg_motion / 30) * 100, 100)

        return normalized

    def _score_faces(self, face_detections: Dict[float, List[Dict]],
                    start_time: float, end_time: float) -> Tuple[float, int, bool]:
        """
        Score face presence in clip

        Returns:
            (score 0-100, max_num_faces, has_faces)
        """
        # Find face detections in this time range
        relevant_detections = [
            faces for timestamp, faces in face_detections.items()
            if start_time <= timestamp <= end_time
        ]

        if not relevant_detections:
            return (0, 0, False)

        # Calculate face scores
        face_scores = []
        max_faces = 0

        for faces in relevant_detections:
            score = self.face_detector.score_frame_by_faces(faces)
            face_scores.append(score)
            max_faces = max(max_faces, len(faces))

        avg_score = np.mean(face_scores)

        # Normalize to 0-100
        # Max expected score is around 100 (from score_frame_by_faces)
        normalized_score = min(avg_score, 100)

        return (normalized_score, max_faces, True)

    def _remove_overlaps(self, moments: List[MomentScore],
                        min_gap: float = 1.0) -> List[MomentScore]:
        """
        Remove overlapping moments, keeping highest scoring

        Args:
            moments: List of scored moments
            min_gap: Minimum gap between clips

        Returns:
            List of non-overlapping moments
        """
        if not moments:
            return []

        # Sort by score
        sorted_moments = sorted(moments, key=lambda m: m.total_score, reverse=True)

        selected = [sorted_moments[0]]

        for moment in sorted_moments[1:]:
            # Check if this moment overlaps with any selected moment
            overlaps = False
            for selected_moment in selected:
                if not (moment.end_time < selected_moment.start_time - min_gap or
                       moment.start_time > selected_moment.end_time + min_gap):
                    overlaps = True
                    break

            if not overlaps:
                selected.append(moment)

        # Sort by time for final output
        selected.sort(key=lambda m: m.start_time)

        return selected

    def score_image(self, image_path: Path) -> Dict:
        """
        Score an image for quality and face presence

        Args:
            image_path: Path to image file

        Returns:
            Dictionary with scores
        """
        logger.info(f"Scoring image: {image_path}")

        # Load image
        img = cv2.imread(str(image_path))
        if img is None:
            return {'error': 'Could not load image'}

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Quality metrics
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        sharpness = laplacian.var()
        brightness = np.mean(gray)
        contrast = np.std(gray)

        quality_score = (
            min(sharpness / 10, 100) * 0.4 +
            min(abs(brightness - 128) / 1.28, 100) * 0.3 +
            min(contrast / 0.5, 100) * 0.3
        )

        # Face detection
        faces = self.face_detector.detect_faces_in_image(image_path)
        face_score = self.face_detector.score_frame_by_faces(faces)

        return {
            'quality_score': quality_score,
            'face_score': face_score,
            'has_faces': len(faces) > 0,
            'num_faces': len(faces),
            'sharpness': sharpness,
            'brightness': brightness,
            'contrast': contrast
        }

    def close(self):
        """Clean up resources"""
        self.face_detector.close()
