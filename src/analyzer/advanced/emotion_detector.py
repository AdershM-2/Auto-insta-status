"""
Emotion detection from faces in videos
Requires: pip install -r requirements-advanced.txt
"""
import cv2
import numpy as np
from pathlib import Path
from typing import List, Dict, Tuple
from collections import Counter

from src.utils.config import Config
from src.utils.helpers import get_logger

logger = get_logger(__name__)

try:
    from fer import FER
    EMOTION_AVAILABLE = True
except ImportError:
    EMOTION_AVAILABLE = False
    logger.warning("Emotion detection not available. Install with: pip install -r requirements-advanced.txt")


class EmotionDetector:
    """
    Detects emotions in faces using FER (Facial Expression Recognition)
    Can find moments with specific emotions (happiness, surprise, etc.)
    """

    EMOTIONS = ['angry', 'disgust', 'fear', 'happy', 'sad', 'surprise', 'neutral']

    def __init__(self, use_mtcnn: bool = None):
        """
        Initialize emotion detector

        Args:
            use_mtcnn: Use MTCNN for face detection (more accurate but slower)
        """
        if not EMOTION_AVAILABLE:
            raise ImportError("FER not installed. Run: pip install -r requirements-advanced.txt")

        use_mtcnn = use_mtcnn if use_mtcnn is not None else Config.EMOTION_DETECTION_MTCNN

        logger.info(f"Loading emotion detector (MTCNN: {use_mtcnn})")

        self.detector = FER(mtcnn=use_mtcnn)

        logger.info("✓ Emotion detector loaded")

    def detect_emotions_in_frame(self, frame: np.ndarray) -> List[Dict]:
        """
        Detect emotions in a single frame

        Args:
            frame: Image frame (BGR from OpenCV)

        Returns:
            List of detected emotions with scores and bounding boxes
        """
        # FER expects RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Detect emotions
        result = self.detector.detect_emotions(frame_rgb)

        return result if result else []

    def get_dominant_emotion(self, emotion_scores: Dict[str, float]) -> Tuple[str, float]:
        """
        Get the dominant emotion from scores

        Args:
            emotion_scores: Dictionary of emotion scores

        Returns:
            Tuple of (emotion_name, score)
        """
        if not emotion_scores:
            return ('neutral', 0.0)

        dominant = max(emotion_scores.items(), key=lambda x: x[1])
        return dominant

    def analyze_video_emotions(self, video_path: Path,
                               sample_rate: int = 30) -> Dict:
        """
        Analyze emotions throughout a video

        Args:
            video_path: Path to video file
            sample_rate: Analyze every N frames

        Returns:
            Dictionary with emotion analysis
        """
        logger.info(f"Analyzing emotions in: {video_path}")

        cap = cv2.VideoCapture(str(video_path))
        fps = cap.get(cv2.CAP_PROP_FPS)

        emotion_timeline = []
        all_emotions = []
        frame_idx = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            if frame_idx % sample_rate == 0:
                timestamp = frame_idx / fps

                # Detect emotions
                detections = self.detect_emotions_in_frame(frame)

                if detections:
                    for detection in detections:
                        emotions = detection['emotions']
                        dominant_emotion, score = self.get_dominant_emotion(emotions)

                        emotion_timeline.append({
                            'timestamp': timestamp,
                            'emotion': dominant_emotion,
                            'score': score,
                            'all_emotions': emotions,
                            'bbox': detection['box']
                        })

                        all_emotions.append(dominant_emotion)

            frame_idx += 1

        cap.release()

        # Aggregate results
        emotion_counts = Counter(all_emotions)
        most_common_emotion = emotion_counts.most_common(1)[0] if emotion_counts else ('neutral', 0)

        logger.info(f"✓ Analyzed {len(emotion_timeline)} frames")
        logger.info(f"Most common emotion: {most_common_emotion[0]}")

        return {
            'timeline': emotion_timeline,
            'emotion_counts': dict(emotion_counts),
            'most_common': most_common_emotion,
            'total_detections': len(emotion_timeline)
        }

    def find_happy_moments(self, video_path: Path,
                          threshold: float = 0.5,
                          min_duration: float = 1.0) -> List[Dict]:
        """
        Find moments where people are smiling/happy

        Args:
            video_path: Path to video
            threshold: Happiness score threshold (0-1)
            min_duration: Minimum duration of happy moment

        Returns:
            List of happy moments with timing
        """
        logger.info(f"Finding happy moments (threshold={threshold})")

        analysis = self.analyze_video_emotions(video_path)

        happy_moments = []
        current_moment = None

        for item in analysis['timeline']:
            is_happy = (item['emotion'] == 'happy' and item['score'] >= threshold)

            if is_happy:
                if current_moment is None:
                    # Start new happy moment
                    current_moment = {
                        'start': item['timestamp'],
                        'end': item['timestamp'],
                        'max_score': item['score']
                    }
                else:
                    # Extend current moment
                    current_moment['end'] = item['timestamp']
                    current_moment['max_score'] = max(current_moment['max_score'], item['score'])
            else:
                if current_moment is not None:
                    # End current moment
                    duration = current_moment['end'] - current_moment['start']
                    if duration >= min_duration:
                        current_moment['duration'] = duration
                        happy_moments.append(current_moment)

                    current_moment = None

        # Don't forget last moment
        if current_moment is not None:
            duration = current_moment['end'] - current_moment['start']
            if duration >= min_duration:
                current_moment['duration'] = duration
                happy_moments.append(current_moment)

        logger.info(f"✓ Found {len(happy_moments)} happy moments")
        return happy_moments

    def find_moments_by_emotion(self, video_path: Path,
                                emotion: str,
                                threshold: float = 0.5) -> List[Dict]:
        """
        Find moments with a specific emotion

        Args:
            video_path: Path to video
            emotion: Emotion to find (happy, sad, surprise, etc.)
            threshold: Score threshold

        Returns:
            List of moments with the emotion
        """
        if emotion not in self.EMOTIONS:
            raise ValueError(f"Unknown emotion: {emotion}. Valid: {self.EMOTIONS}")

        logger.info(f"Finding '{emotion}' moments")

        analysis = self.analyze_video_emotions(video_path)

        moments = []

        for item in analysis['timeline']:
            emotion_score = item['all_emotions'].get(emotion, 0)

            if emotion_score >= threshold:
                moments.append({
                    'timestamp': item['timestamp'],
                    'score': emotion_score,
                    'dominant_emotion': item['emotion']
                })

        logger.info(f"✓ Found {len(moments)} '{emotion}' moments")
        return moments

    def score_frame_by_positive_emotion(self, frame: np.ndarray) -> float:
        """
        Score a frame by positive emotions (happy, surprise)

        Args:
            frame: Image frame

        Returns:
            Positivity score (0-100)
        """
        detections = self.detect_emotions_in_frame(frame)

        if not detections:
            return 0.0

        positive_emotions = ['happy', 'surprise']
        positive_scores = []

        for detection in detections:
            emotions = detection['emotions']
            positive_score = sum(emotions.get(e, 0) for e in positive_emotions)
            positive_scores.append(positive_score)

        # Average across all detected faces
        avg_positive = np.mean(positive_scores) if positive_scores else 0

        # Convert to 0-100 scale
        return avg_positive * 100

    def get_emotion_statistics(self, video_path: Path) -> Dict:
        """
        Get overall emotion statistics for a video

        Args:
            video_path: Path to video

        Returns:
            Dictionary with emotion statistics
        """
        analysis = self.analyze_video_emotions(video_path)

        timeline = analysis['timeline']

        if not timeline:
            return {
                'average_happiness': 0,
                'average_positivity': 0,
                'emotion_distribution': {},
                'mood': 'neutral'
            }

        # Calculate averages
        happiness_scores = [
            item['all_emotions'].get('happy', 0)
            for item in timeline
        ]

        positivity_scores = [
            item['all_emotions'].get('happy', 0) +
            item['all_emotions'].get('surprise', 0)
            for item in timeline
        ]

        avg_happiness = np.mean(happiness_scores) * 100
        avg_positivity = np.mean(positivity_scores) * 100

        # Determine overall mood
        if avg_positivity > 50:
            mood = 'positive'
        elif avg_positivity > 30:
            mood = 'neutral'
        else:
            mood = 'negative'

        return {
            'average_happiness': avg_happiness,
            'average_positivity': avg_positivity,
            'emotion_distribution': analysis['emotion_counts'],
            'mood': mood,
            'most_common_emotion': analysis['most_common'][0]
        }
