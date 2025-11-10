"""
Face detection using MediaPipe for intelligent framing
"""
import cv2
import numpy as np
from pathlib import Path
from typing import List, Tuple, Dict, Optional
import mediapipe as mp

from src.utils.config import Config
from src.utils.helpers import get_logger

logger = get_logger(__name__)


class FaceDetector:
    """
    Detects faces in images and videos using MediaPipe
    """

    def __init__(self):
        """Initialize MediaPipe face detection"""
        self.mp_face_detection = mp.solutions.face_detection
        self.face_detection = self.mp_face_detection.FaceDetection(
            min_detection_confidence=Config.FACE_DETECTION_CONFIDENCE
        )

    def detect_faces_in_image(self, image_path: Path) -> List[Dict]:
        """
        Detect faces in an image

        Args:
            image_path: Path to image file

        Returns:
            List of face dictionaries with bbox and confidence
        """
        image = cv2.imread(str(image_path))
        if image is None:
            logger.error(f"Could not read image: {image_path}")
            return []

        # Convert BGR to RGB
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Detect faces
        results = self.face_detection.process(image_rgb)

        faces = []
        if results.detections:
            h, w = image.shape[:2]
            for detection in results.detections:
                bbox = detection.location_data.relative_bounding_box
                faces.append({
                    'bbox': {
                        'x': int(bbox.xmin * w),
                        'y': int(bbox.ymin * h),
                        'width': int(bbox.width * w),
                        'height': int(bbox.height * h)
                    },
                    'confidence': detection.score[0],
                    'center': (
                        int((bbox.xmin + bbox.width / 2) * w),
                        int((bbox.ymin + bbox.height / 2) * h)
                    )
                })

        logger.info(f"Detected {len(faces)} face(s) in {image_path}")
        return faces

    def detect_faces_in_video(self, video_path: Path,
                              sample_rate: int = 30) -> Dict[float, List[Dict]]:
        """
        Detect faces in video at sampled intervals

        Args:
            video_path: Path to video file
            sample_rate: Sample every N frames

        Returns:
            Dictionary mapping timestamp to list of face detections
        """
        logger.info(f"Detecting faces in video: {video_path}")

        cap = cv2.VideoCapture(str(video_path))
        fps = cap.get(cv2.CAP_PROP_FPS)

        detections = {}
        frame_idx = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Sample frames
            if frame_idx % sample_rate == 0:
                timestamp = frame_idx / fps

                # Convert BGR to RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                # Detect faces
                results = self.face_detection.process(frame_rgb)

                faces = []
                if results.detections:
                    h, w = frame.shape[:2]
                    for detection in results.detections:
                        bbox = detection.location_data.relative_bounding_box
                        faces.append({
                            'bbox': {
                                'x': int(bbox.xmin * w),
                                'y': int(bbox.ymin * h),
                                'width': int(bbox.width * w),
                                'height': int(bbox.height * h)
                            },
                            'confidence': detection.score[0],
                            'center': (
                                int((bbox.xmin + bbox.width / 2) * w),
                                int((bbox.ymin + bbox.height / 2) * h)
                            )
                        })

                if faces:
                    detections[timestamp] = faces

            frame_idx += 1

        cap.release()

        logger.info(f"✓ Detected faces at {len(detections)} timestamps")
        return detections

    def get_face_center(self, faces: List[Dict]) -> Optional[Tuple[int, int]]:
        """
        Get the center point of all detected faces

        Args:
            faces: List of face detections

        Returns:
            (x, y) center point or None if no faces
        """
        if not faces:
            return None

        # Average center of all faces
        centers = [face['center'] for face in faces]
        avg_x = int(np.mean([c[0] for c in centers]))
        avg_y = int(np.mean([c[1] for c in centers]))

        return (avg_x, avg_y)

    def calculate_smart_crop(self, image_shape: Tuple[int, int],
                            faces: List[Dict]) -> Tuple[int, int, int, int]:
        """
        Calculate optimal crop region to keep faces centered in 9:16 format

        Args:
            image_shape: (height, width) of original image
            faces: List of face detections

        Returns:
            (x1, y1, x2, y2) crop coordinates
        """
        h, w = image_shape[:2]
        target_aspect = Config.TARGET_HEIGHT / Config.TARGET_WIDTH  # 16:9 = 1.777

        if not faces:
            # No faces, crop from center
            if h / w > target_aspect:
                # Image is taller
                new_h = int(w * target_aspect)
                y1 = (h - new_h) // 2
                return (0, y1, w, y1 + new_h)
            else:
                # Image is wider
                new_w = int(h / target_aspect)
                x1 = (w - new_w) // 2
                return (x1, 0, x1 + new_w, h)

        # Get face center
        face_center = self.get_face_center(faces)
        if not face_center:
            # Fallback to center crop
            if h / w > target_aspect:
                new_h = int(w * target_aspect)
                y1 = (h - new_h) // 2
                return (0, y1, w, y1 + new_h)
            else:
                new_w = int(h / target_aspect)
                x1 = (w - new_w) // 2
                return (x1, 0, x1 + new_w, h)

        cx, cy = face_center

        # Calculate crop region keeping face centered
        if h / w > target_aspect:
            # Image is taller - fit width, crop height
            new_h = int(w * target_aspect)
            # Center on face y position
            y1 = max(0, min(cy - new_h // 2, h - new_h))
            return (0, y1, w, y1 + new_h)
        else:
            # Image is wider - fit height, crop width
            new_w = int(h / target_aspect)
            # Center on face x position
            x1 = max(0, min(cx - new_w // 2, w - new_w))
            return (x1, 0, x1 + new_w, h)

    def score_frame_by_faces(self, faces: List[Dict]) -> float:
        """
        Score a frame based on face detection quality

        Args:
            faces: List of face detections

        Returns:
            Score (higher = better)
        """
        if not faces:
            return 0.0

        # Score based on:
        # - Number of faces (more = better, up to 3)
        # - Confidence scores
        # - Face sizes (larger = better)

        num_faces = min(len(faces), 3)
        avg_confidence = np.mean([f['confidence'] for f in faces])
        avg_size = np.mean([f['bbox']['width'] * f['bbox']['height'] for f in faces])

        # Normalize size to 0-1 range (assuming max face size is 1/4 of frame)
        normalized_size = min(avg_size / (Config.TARGET_WIDTH * Config.TARGET_HEIGHT * 0.25), 1.0)

        # Combined score
        score = (num_faces * 20) + (avg_confidence * 50) + (normalized_size * 30)

        return score

    def close(self):
        """Clean up resources"""
        self.face_detection.close()
