"""
CLIP-based semantic scene understanding
Requires: pip install -r requirements-medium.txt
"""
import cv2
import torch
import numpy as np
from pathlib import Path
from typing import List, Dict, Tuple
from PIL import Image

from src.utils.config import Config
from src.utils.helpers import get_logger

logger = get_logger(__name__)

try:
    import open_clip
    CLIP_AVAILABLE = True
except ImportError:
    CLIP_AVAILABLE = False
    logger.warning("CLIP not available. Install with: pip install -r requirements-medium.txt")


class CLIPAnalyzer:
    """
    Uses CLIP to understand image/video content semantically
    Enables queries like "find beach scenes" or "find people laughing"
    """

    def __init__(self, model_name: str = None, pretrained: str = None):
        """
        Initialize CLIP model

        Args:
            model_name: CLIP model name (default: ViT-B-32)
            pretrained: Pretrained weights (default: openai)
        """
        if not CLIP_AVAILABLE:
            raise ImportError("CLIP not installed. Run: pip install -r requirements-medium.txt")

        self.model_name = model_name or Config.CLIP_MODEL
        self.pretrained = pretrained or Config.CLIP_PRETRAINED

        logger.info(f"Loading CLIP model: {self.model_name}")

        # Load model
        self.model, _, self.preprocess = open_clip.create_model_and_transforms(
            self.model_name,
            pretrained=self.pretrained
        )
        self.tokenizer = open_clip.get_tokenizer(self.model_name)

        # Move to GPU if available
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = self.model.to(self.device)
        self.model.eval()

        logger.info(f"✓ CLIP model loaded on {self.device}")

    def encode_image(self, image: np.ndarray) -> torch.Tensor:
        """
        Encode image to CLIP embedding

        Args:
            image: Image as numpy array (BGR from OpenCV)

        Returns:
            Image embedding tensor
        """
        # Convert BGR to RGB
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(image_rgb)

        # Preprocess and encode
        image_input = self.preprocess(pil_image).unsqueeze(0).to(self.device)

        with torch.no_grad():
            image_features = self.model.encode_image(image_input)
            image_features /= image_features.norm(dim=-1, keepdim=True)

        return image_features

    def encode_text(self, text: str) -> torch.Tensor:
        """
        Encode text to CLIP embedding

        Args:
            text: Text description

        Returns:
            Text embedding tensor
        """
        text_input = self.tokenizer([text]).to(self.device)

        with torch.no_grad():
            text_features = self.model.encode_text(text_input)
            text_features /= text_features.norm(dim=-1, keepdim=True)

        return text_features

    def similarity(self, image_features: torch.Tensor,
                   text_features: torch.Tensor) -> float:
        """
        Calculate similarity between image and text

        Args:
            image_features: Image embedding
            text_features: Text embedding

        Returns:
            Similarity score (0-1)
        """
        similarity = (image_features @ text_features.T).item()
        # Convert from [-1, 1] to [0, 1]
        similarity = (similarity + 1) / 2
        return similarity

    def find_matching_frames(self,
                            video_path: Path,
                            query: str,
                            threshold: float = 0.3,
                            sample_rate: int = 30) -> List[Tuple[float, float]]:
        """
        Find frames in video that match text query

        Args:
            video_path: Path to video file
            query: Text query (e.g., "beach sunset", "people laughing")
            threshold: Similarity threshold (0-1)
            sample_rate: Sample every N frames

        Returns:
            List of (timestamp, similarity_score) tuples
        """
        logger.info(f"Searching for '{query}' in {video_path}")

        cap = cv2.VideoCapture(str(video_path))
        fps = cap.get(cv2.CAP_PROP_FPS)

        # Encode query text once
        text_features = self.encode_text(query)

        matching_frames = []
        frame_idx = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Sample frames
            if frame_idx % sample_rate == 0:
                timestamp = frame_idx / fps

                # Encode frame
                image_features = self.encode_image(frame)

                # Calculate similarity
                sim = self.similarity(image_features, text_features)

                if sim >= threshold:
                    matching_frames.append((timestamp, sim))
                    logger.debug(f"Match at {timestamp:.2f}s: {sim:.3f}")

            frame_idx += 1

        cap.release()

        logger.info(f"✓ Found {len(matching_frames)} matching frames")
        return matching_frames

    def rank_images_by_query(self,
                            image_paths: List[Path],
                            query: str) -> List[Tuple[Path, float]]:
        """
        Rank images by how well they match a query

        Args:
            image_paths: List of image paths
            query: Text query

        Returns:
            List of (image_path, score) tuples, sorted by score
        """
        logger.info(f"Ranking {len(image_paths)} images by: '{query}'")

        # Encode query
        text_features = self.encode_text(query)

        scores = []

        for img_path in image_paths:
            # Load image
            image = cv2.imread(str(img_path))
            if image is None:
                continue

            # Encode image
            image_features = self.encode_image(image)

            # Calculate similarity
            score = self.similarity(image_features, text_features)
            scores.append((img_path, score))

        # Sort by score
        scores.sort(key=lambda x: x[1], reverse=True)

        logger.info(f"✓ Ranked images, top score: {scores[0][1]:.3f}")
        return scores

    def classify_scene(self, image: np.ndarray,
                      categories: List[str]) -> Dict[str, float]:
        """
        Classify image into multiple categories

        Args:
            image: Image as numpy array
            categories: List of category names

        Returns:
            Dictionary mapping category to score
        """
        # Encode image
        image_features = self.encode_image(image)

        # Encode all categories
        category_features = torch.cat([
            self.encode_text(cat) for cat in categories
        ])

        # Calculate similarities
        similarities = (image_features @ category_features.T)[0]

        # Softmax to get probabilities
        probs = torch.softmax(similarities, dim=0)

        # Return as dict
        results = {cat: prob.item() for cat, prob in zip(categories, probs)}

        return results

    def suggest_descriptions(self, image: np.ndarray,
                           candidates: List[str]) -> List[Tuple[str, float]]:
        """
        Given multiple description candidates, rank them by relevance

        Args:
            image: Image as numpy array
            candidates: List of possible descriptions

        Returns:
            List of (description, score) tuples, sorted by relevance
        """
        image_features = self.encode_image(image)

        scores = []
        for desc in candidates:
            text_features = self.encode_text(desc)
            score = self.similarity(image_features, text_features)
            scores.append((desc, score))

        scores.sort(key=lambda x: x[1], reverse=True)
        return scores

    def analyze_video_content(self, video_path: Path,
                             sample_rate: int = 30) -> Dict:
        """
        Analyze overall video content using CLIP

        Args:
            video_path: Path to video
            sample_rate: Sample every N frames

        Returns:
            Dictionary with content analysis
        """
        logger.info(f"Analyzing video content: {video_path}")

        # Common scene categories
        categories = [
            "indoor scene", "outdoor scene", "nature", "urban",
            "people", "portrait", "landscape", "food", "animals",
            "sunset", "beach", "mountain", "city", "party",
            "sport", "travel", "product", "text"
        ]

        cap = cv2.VideoCapture(str(video_path))
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        # Sample frames and analyze
        category_scores = {cat: [] for cat in categories}
        frame_idx = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            if frame_idx % sample_rate == 0:
                # Classify frame
                results = self.classify_scene(frame, categories)

                # Accumulate scores
                for cat, score in results.items():
                    category_scores[cat].append(score)

            frame_idx += 1

        cap.release()

        # Average scores
        avg_scores = {
            cat: np.mean(scores) if scores else 0
            for cat, scores in category_scores.items()
        }

        # Get top categories
        top_categories = sorted(avg_scores.items(), key=lambda x: x[1], reverse=True)[:5]

        logger.info(f"✓ Top categories: {[cat for cat, _ in top_categories]}")

        return {
            'categories': avg_scores,
            'top_categories': top_categories,
            'frames_analyzed': frame_idx // sample_rate
        }
