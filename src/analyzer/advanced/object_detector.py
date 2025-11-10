"""
Advanced object detection and tracking using YOLO
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
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False
    logger.warning("YOLO not available. Install with: pip install -r requirements-advanced.txt")


class ObjectDetector:
    """
    Detects and tracks objects in videos using YOLOv8
    Can identify people, animals, vehicles, and 80+ object classes
    """

    # Common COCO classes
    PERSON_CLASS = 0
    CAR_CLASS = 2
    DOG_CLASS = 16
    CAT_CLASS = 15

    def __init__(self, model_size: str = 'n'):
        """
        Initialize YOLO model

        Args:
            model_size: Model size (n=nano, s=small, m=medium, l=large, x=xlarge)
                       nano is fastest, xlarge is most accurate
        """
        if not YOLO_AVAILABLE:
            raise ImportError("YOLO not installed. Run: pip install -r requirements-advanced.txt")

        model_name = f"yolov8{model_size}.pt"

        logger.info(f"Loading YOLO model: {model_name}")
        logger.info("First load will download the model")

        self.model = YOLO(model_name)

        logger.info(f"✓ YOLO model loaded")

    def detect_objects_in_frame(self, frame: np.ndarray,
                                confidence: float = 0.5) -> List[Dict]:
        """
        Detect objects in a single frame

        Args:
            frame: Image frame (BGR from OpenCV)
            confidence: Detection confidence threshold

        Returns:
            List of detected objects with bounding boxes and classes
        """
        # Run detection
        results = self.model(frame, conf=confidence, verbose=False)

        detections = []

        for result in results:
            boxes = result.boxes

            for i in range(len(boxes)):
                box = boxes[i]

                detections.append({
                    'class_id': int(box.cls[0]),
                    'class_name': result.names[int(box.cls[0])],
                    'confidence': float(box.conf[0]),
                    'bbox': box.xyxy[0].tolist()  # [x1, y1, x2, y2]
                })

        return detections

    def count_people_in_video(self, video_path: Path,
                             sample_rate: int = 30) -> Dict:
        """
        Count people throughout video

        Args:
            video_path: Path to video
            sample_rate: Analyze every N frames

        Returns:
            Dictionary with people count statistics
        """
        logger.info(f"Counting people in: {video_path}")

        cap = cv2.VideoCapture(str(video_path))
        fps = cap.get(cv2.CAP_PROP_FPS)

        people_counts = []
        frame_idx = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            if frame_idx % sample_rate == 0:
                timestamp = frame_idx / fps

                # Detect objects
                detections = self.detect_objects_in_frame(frame)

                # Count people
                num_people = sum(1 for d in detections if d['class_id'] == self.PERSON_CLASS)

                people_counts.append({
                    'timestamp': timestamp,
                    'count': num_people
                })

            frame_idx += 1

        cap.release()

        # Calculate statistics
        counts = [pc['count'] for pc in people_counts]
        avg_people = np.mean(counts) if counts else 0
        max_people = max(counts) if counts else 0

        logger.info(f"✓ Average people per frame: {avg_people:.1f}, Max: {max_people}")

        return {
            'timeline': people_counts,
            'average': avg_people,
            'max': max_people,
            'frames_analyzed': len(people_counts)
        }

    def find_object_appearances(self, video_path: Path,
                               object_names: List[str],
                               confidence: float = 0.5) -> Dict[str, List[float]]:
        """
        Find when specific objects appear in video

        Args:
            video_path: Path to video
            object_names: List of object names to find (e.g., ['dog', 'cat', 'car'])
            confidence: Detection confidence threshold

        Returns:
            Dictionary mapping object name to list of timestamps
        """
        logger.info(f"Finding objects: {object_names}")

        cap = cv2.VideoCapture(str(video_path))
        fps = cap.get(cv2.CAP_PROP_FPS)

        object_appearances = {obj: [] for obj in object_names}
        frame_idx = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            timestamp = frame_idx / fps

            # Detect objects
            detections = self.detect_objects_in_frame(frame, confidence)

            # Check for target objects
            detected_objects = set(d['class_name'] for d in detections)

            for obj in object_names:
                if obj in detected_objects:
                    object_appearances[obj].append(timestamp)

            frame_idx += 1

        cap.release()

        for obj, timestamps in object_appearances.items():
            logger.info(f"'{obj}' appeared in {len(timestamps)} frames")

        return object_appearances

    def get_scene_objects(self, video_path: Path,
                         sample_rate: int = 60) -> Dict:
        """
        Get all objects detected throughout video

        Args:
            video_path: Path to video
            sample_rate: Analyze every N frames

        Returns:
            Dictionary with object statistics
        """
        logger.info(f"Detecting all objects in: {video_path}")

        cap = cv2.VideoCapture(str(video_path))

        all_objects = []
        frame_idx = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            if frame_idx % sample_rate == 0:
                # Detect objects
                detections = self.detect_objects_in_frame(frame)

                for detection in detections:
                    all_objects.append(detection['class_name'])

            frame_idx += 1

        cap.release()

        # Count occurrences
        object_counts = Counter(all_objects)

        logger.info(f"✓ Detected {len(object_counts)} unique object types")

        return {
            'object_counts': dict(object_counts),
            'most_common': object_counts.most_common(10),
            'total_detections': len(all_objects)
        }

    def find_action_shots(self, video_path: Path,
                         action_objects: List[str] = None) -> List[Dict]:
        """
        Find dynamic/action shots with specific objects

        Args:
            video_path: Path to video
            action_objects: Objects that indicate action (e.g., 'sports ball', 'bicycle')

        Returns:
            List of action shots with timestamps
        """
        if action_objects is None:
            action_objects = [
                'sports ball', 'bicycle', 'skateboard', 'surfboard',
                'tennis racket', 'baseball bat', 'skis', 'snowboard'
            ]

        logger.info("Finding action shots")

        appearances = self.find_object_appearances(video_path, action_objects)

        action_shots = []

        for obj, timestamps in appearances.items():
            for ts in timestamps:
                action_shots.append({
                    'timestamp': ts,
                    'object': obj,
                    'type': 'action'
                })

        # Sort by timestamp
        action_shots.sort(key=lambda x: x['timestamp'])

        logger.info(f"✓ Found {len(action_shots)} potential action shots")

        return action_shots

    def score_frame_by_content(self, frame: np.ndarray) -> float:
        """
        Score a frame by content richness

        Args:
            frame: Image frame

        Returns:
            Content score (0-100)
        """
        detections = self.detect_objects_in_frame(frame)

        if not detections:
            return 0

        # Score based on:
        # - Number of objects (more = higher score)
        # - Average confidence
        # - Presence of people (bonus)

        num_objects = len(detections)
        avg_confidence = np.mean([d['confidence'] for d in detections])
        has_people = any(d['class_id'] == self.PERSON_CLASS for d in detections)

        # Calculate score
        object_score = min(num_objects * 10, 50)  # Max 50 for objects
        confidence_score = avg_confidence * 30  # Max 30 for confidence
        people_bonus = 20 if has_people else 0  # 20 bonus for people

        total_score = object_score + confidence_score + people_bonus

        return min(total_score, 100)

    def get_frame_focus_point(self, frame: np.ndarray) -> Tuple[int, int]:
        """
        Get the optimal focus point based on detected objects

        Args:
            frame: Image frame

        Returns:
            (x, y) coordinates of focus point
        """
        detections = self.detect_objects_in_frame(frame)

        if not detections:
            # Default to center
            h, w = frame.shape[:2]
            return (w // 2, h // 2)

        # Prioritize people, then other objects
        people = [d for d in detections if d['class_id'] == self.PERSON_CLASS]

        if people:
            # Focus on people
            target_detections = people
        else:
            # Focus on most confident detection
            target_detections = [max(detections, key=lambda d: d['confidence'])]

        # Calculate center of bounding boxes
        centers = []
        for d in target_detections:
            bbox = d['bbox']
            cx = (bbox[0] + bbox[2]) / 2
            cy = (bbox[1] + bbox[3]) / 2
            centers.append((cx, cy))

        # Average center
        avg_x = int(np.mean([c[0] for c in centers]))
        avg_y = int(np.mean([c[1] for c in centers]))

        return (avg_x, avg_y)

    @staticmethod
    def get_available_classes() -> List[str]:
        """Get list of all object classes YOLO can detect"""
        # COCO dataset classes
        return [
            'person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus', 'train',
            'truck', 'boat', 'traffic light', 'fire hydrant', 'stop sign',
            'parking meter', 'bench', 'bird', 'cat', 'dog', 'horse', 'sheep',
            'cow', 'elephant', 'bear', 'zebra', 'giraffe', 'backpack', 'umbrella',
            'handbag', 'tie', 'suitcase', 'frisbee', 'skis', 'snowboard',
            'sports ball', 'kite', 'baseball bat', 'baseball glove', 'skateboard',
            'surfboard', 'tennis racket', 'bottle', 'wine glass', 'cup', 'fork',
            'knife', 'spoon', 'bowl', 'banana', 'apple', 'sandwich', 'orange',
            'broccoli', 'carrot', 'hot dog', 'pizza', 'donut', 'cake', 'chair',
            'couch', 'potted plant', 'bed', 'dining table', 'toilet', 'tv',
            'laptop', 'mouse', 'remote', 'keyboard', 'cell phone', 'microwave',
            'oven', 'toaster', 'sink', 'refrigerator', 'book', 'clock', 'vase',
            'scissors', 'teddy bear', 'hair drier', 'toothbrush'
        ]
