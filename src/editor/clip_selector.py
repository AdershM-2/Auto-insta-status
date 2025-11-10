"""
Intelligent clip selection using AI analysis
"""
from pathlib import Path
from typing import List, Dict, Tuple
from dataclasses import dataclass
from moviepy.editor import VideoFileClip, ImageClip

from src.utils.config import Config
from src.utils.helpers import get_logger
from src.analyzer import MomentScorer

logger = get_logger(__name__)


@dataclass
class SelectedClip:
    """Represents a selected clip with metadata"""
    source_path: Path
    clip_type: str  # 'image' or 'video'
    start_time: float = 0
    end_time: float = 0
    duration: float = 0
    score: float = 0
    has_faces: bool = False
    order: int = 0


class ClipSelector:
    """
    Intelligently selects and orders clips from images and videos
    """

    def __init__(self):
        self.scorer = MomentScorer()

    def select_clips(self,
                    images: List[Path],
                    videos: List[Path],
                    target_duration: float,
                    description: str = "") -> List[SelectedClip]:
        """
        Intelligently select clips from provided media

        Args:
            images: List of image paths
            videos: List of video paths
            target_duration: Target total duration in seconds
            description: User description to guide selection

        Returns:
            List of SelectedClip objects in optimal order
        """
        logger.info(f"Selecting clips for {target_duration}s reel")
        logger.info(f"Input: {len(images)} images, {len(videos)} videos")

        selected_clips = []

        # Score and select from videos
        video_clips = self._select_from_videos(videos, target_duration * 0.6)
        selected_clips.extend(video_clips)

        # Score and select from images
        image_clips = self._select_from_images(images, target_duration * 0.4)
        selected_clips.extend(image_clips)

        # Adjust durations to fit target
        selected_clips = self._adjust_durations(selected_clips, target_duration)

        # Order clips intelligently
        ordered_clips = self._order_clips(selected_clips, description)

        logger.info(f"✓ Selected {len(ordered_clips)} clips totaling {sum(c.duration for c in ordered_clips):.1f}s")

        return ordered_clips

    def _select_from_videos(self, videos: List[Path],
                           target_duration: float) -> List[SelectedClip]:
        """
        Select best moments from videos

        Args:
            videos: List of video paths
            target_duration: Target total duration from videos

        Returns:
            List of SelectedClip objects
        """
        if not videos:
            return []

        logger.info(f"Analyzing {len(videos)} videos...")

        selected = []

        for video_path in videos:
            # Get video duration
            with VideoFileClip(str(video_path)) as clip:
                video_duration = clip.duration

            if video_duration < Config.MIN_CLIP_DURATION:
                logger.warning(f"Video too short, skipping: {video_path}")
                continue

            # Determine how many clips to extract
            clips_per_video = max(1, int(target_duration / len(videos) / Config.MIN_CLIP_DURATION))

            # Score and select best moments
            moments = self.scorer.score_video(
                video_path,
                num_clips=clips_per_video,
                clip_duration=min(Config.MAX_CLIP_DURATION, target_duration / clips_per_video)
            )

            # Convert to SelectedClip objects
            for moment in moments:
                selected.append(SelectedClip(
                    source_path=video_path,
                    clip_type='video',
                    start_time=moment.start_time,
                    end_time=moment.end_time,
                    duration=moment.end_time - moment.start_time,
                    score=moment.total_score,
                    has_faces=moment.has_faces
                ))

        # Sort by score and select best clips
        selected.sort(key=lambda c: c.score, reverse=True)

        # Select clips that fit target duration
        final_selected = []
        total_duration = 0

        for clip in selected:
            if total_duration + clip.duration <= target_duration:
                final_selected.append(clip)
                total_duration += clip.duration
            else:
                # Try to fit a shorter version
                remaining = target_duration - total_duration
                if remaining >= Config.MIN_CLIP_DURATION:
                    clip.end_time = clip.start_time + remaining
                    clip.duration = remaining
                    final_selected.append(clip)
                break

        logger.info(f"Selected {len(final_selected)} video clips ({total_duration:.1f}s)")
        return final_selected

    def _select_from_images(self, images: List[Path],
                           target_duration: float) -> List[SelectedClip]:
        """
        Select and score images

        Args:
            images: List of image paths
            target_duration: Target total duration from images

        Returns:
            List of SelectedClip objects
        """
        if not images:
            return []

        logger.info(f"Analyzing {len(images)} images...")

        scored_images = []

        for image_path in images:
            score_data = self.scorer.score_image(image_path)

            if 'error' in score_data:
                logger.warning(f"Error scoring {image_path}: {score_data['error']}")
                continue

            # Combined score (quality + faces)
            total_score = score_data['quality_score'] + score_data['face_score']

            scored_images.append({
                'path': image_path,
                'score': total_score,
                'has_faces': score_data['has_faces']
            })

        # Sort by score
        scored_images.sort(key=lambda x: x['score'], reverse=True)

        # Select best images to fit duration
        duration_per_image = min(
            Config.DEFAULT_IMAGE_DURATION,
            target_duration / len(scored_images) if scored_images else Config.DEFAULT_IMAGE_DURATION
        )

        selected = []
        total_duration = 0

        for img_data in scored_images:
            if total_duration + duration_per_image <= target_duration:
                selected.append(SelectedClip(
                    source_path=img_data['path'],
                    clip_type='image',
                    duration=duration_per_image,
                    score=img_data['score'],
                    has_faces=img_data['has_faces']
                ))
                total_duration += duration_per_image
            else:
                break

        logger.info(f"Selected {len(selected)} images ({total_duration:.1f}s)")
        return selected

    def _adjust_durations(self, clips: List[SelectedClip],
                         target_duration: float) -> List[SelectedClip]:
        """
        Adjust clip durations to exactly match target duration

        Args:
            clips: List of SelectedClip objects
            target_duration: Target total duration

        Returns:
            Adjusted list of SelectedClip objects
        """
        if not clips:
            return clips

        current_duration = sum(c.duration for c in clips)

        if abs(current_duration - target_duration) < 0.1:
            # Close enough
            return clips

        # Scale all durations proportionally
        scale_factor = target_duration / current_duration

        for clip in clips:
            if clip.clip_type == 'image':
                clip.duration *= scale_factor
            else:
                # For videos, adjust end_time
                new_duration = clip.duration * scale_factor
                if new_duration >= Config.MIN_CLIP_DURATION:
                    clip.end_time = clip.start_time + new_duration
                    clip.duration = new_duration

        return clips

    def _order_clips(self, clips: List[SelectedClip],
                    description: str = "") -> List[SelectedClip]:
        """
        Order clips intelligently for best flow

        Strategy:
        1. Start with high-scoring clip (hook)
        2. Alternate between different types
        3. Mix clips with/without faces
        4. End with strong clip

        Args:
            clips: List of SelectedClip objects
            description: User description for context

        Returns:
            Ordered list of clips
        """
        if len(clips) <= 2:
            # Too few clips to reorder meaningfully
            for i, clip in enumerate(clips):
                clip.order = i
            return clips

        # Separate by type
        video_clips = [c for c in clips if c.clip_type == 'video']
        image_clips = [c for c in clips if c.clip_type == 'image']

        # Sort each by score
        video_clips.sort(key=lambda c: c.score, reverse=True)
        image_clips.sort(key=lambda c: c.score, reverse=True)

        # Build ordered sequence
        ordered = []

        # Start with best video or image (hook)
        if video_clips and (not image_clips or video_clips[0].score > image_clips[0].score):
            ordered.append(video_clips.pop(0))
        elif image_clips:
            ordered.append(image_clips.pop(0))

        # Alternate between types for variety
        while video_clips or image_clips:
            # Prefer alternating types
            if video_clips and (not image_clips or len(ordered) % 2 == 1):
                ordered.append(video_clips.pop(0))
            elif image_clips:
                ordered.append(image_clips.pop(0))
            elif video_clips:
                ordered.append(video_clips.pop(0))

        # Assign order indices
        for i, clip in enumerate(ordered):
            clip.order = i

        logger.info(f"Ordered {len(ordered)} clips: {sum(1 for c in ordered if c.clip_type == 'video')} videos, {sum(1 for c in ordered if c.clip_type == 'image')} images")

        return ordered

    def close(self):
        """Clean up resources"""
        self.scorer.close()
