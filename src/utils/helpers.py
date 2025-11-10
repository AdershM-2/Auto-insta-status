"""
Helper utility functions
"""
import os
from pathlib import Path
from typing import List, Union
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def get_logger(name: str):
    """Get a logger instance"""
    return logging.getLogger(name)


def parse_file_list(file_string: str) -> List[Path]:
    """
    Parse a comma-separated string of file paths or glob patterns

    Args:
        file_string: Comma-separated file paths or patterns (e.g., "*.jpg,img1.png")

    Returns:
        List of Path objects
    """
    if not file_string:
        return []

    files = []
    for item in file_string.split(','):
        item = item.strip()
        if '*' in item:
            # Handle glob pattern
            import glob
            files.extend([Path(f) for f in glob.glob(item)])
        else:
            path = Path(item)
            if path.exists():
                files.append(path)

    return files


def format_duration(seconds: float) -> str:
    """Format seconds into MM:SS format"""
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes:02d}:{secs:02d}"


def get_video_info(video_path: Union[str, Path]) -> dict:
    """
    Get basic information about a video file

    Returns:
        dict with keys: duration, width, height, fps
    """
    try:
        from moviepy.editor import VideoFileClip

        with VideoFileClip(str(video_path)) as clip:
            return {
                'duration': clip.duration,
                'width': clip.w,
                'height': clip.h,
                'fps': clip.fps,
                'has_audio': clip.audio is not None
            }
    except Exception as e:
        get_logger(__name__).error(f"Error getting video info: {e}")
        return {}


def validate_media_files(images: List[Path], videos: List[Path]) -> bool:
    """
    Validate that media files exist and are readable

    Returns:
        True if all files are valid, False otherwise
    """
    logger = get_logger(__name__)

    valid_image_exts = {'.jpg', '.jpeg', '.png', '.gif', '.bmp'}
    valid_video_exts = {'.mp4', '.mov', '.avi', '.mkv', '.webm'}

    all_valid = True

    for img in images:
        if not img.exists():
            logger.error(f"Image not found: {img}")
            all_valid = False
        elif img.suffix.lower() not in valid_image_exts:
            logger.error(f"Unsupported image format: {img}")
            all_valid = False

    for vid in videos:
        if not vid.exists():
            logger.error(f"Video not found: {vid}")
            all_valid = False
        elif vid.suffix.lower() not in valid_video_exts:
            logger.error(f"Unsupported video format: {vid}")
            all_valid = False

    return all_valid


def calculate_target_duration(num_images: int, num_videos: int,
                              total_video_duration: float,
                              target_duration: int) -> dict:
    """
    Calculate how much time to allocate to images vs videos

    Returns:
        dict with allocation plan
    """
    from src.utils.config import Config

    image_time = num_images * Config.DEFAULT_IMAGE_DURATION
    video_time = total_video_duration
    total_content_time = image_time + video_time

    if total_content_time <= target_duration:
        # Use all content
        return {
            'image_duration_each': Config.DEFAULT_IMAGE_DURATION,
            'video_speed': 1.0,
            'needs_trimming': False
        }
    else:
        # Need to compress
        ratio = target_duration / total_content_time
        return {
            'image_duration_each': Config.DEFAULT_IMAGE_DURATION * ratio,
            'video_speed': 1.0 / ratio,  # Speed up videos
            'needs_trimming': True,
            'compression_ratio': ratio
        }
