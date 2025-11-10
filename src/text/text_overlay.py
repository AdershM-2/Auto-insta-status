"""
Manages text overlays with smart positioning
"""
from typing import List, Dict, Optional, Tuple
from moviepy.editor import CompositeVideoClip, TextClip
import numpy as np

from src.utils.config import Config
from src.utils.helpers import get_logger

logger = get_logger(__name__)


class TextOverlayManager:
    """
    Manages text overlays with intelligent positioning and animations
    """

    def __init__(self):
        self.config = Config()

    def add_captions_to_video(self,
                             video_clip,
                             captions: List[Dict],
                             style: str = "modern") -> CompositeVideoClip:
        """
        Add multiple captions to a video clip

        Args:
            video_clip: VideoFileClip to add text to
            captions: List of caption dicts (text, start_time, duration, position)
            style: Text style (modern, bold, minimal, elegant)

        Returns:
            CompositeVideoClip with text overlays
        """
        logger.info(f"Adding {len(captions)} captions to video")

        if not captions:
            return video_clip

        # Create text clips
        text_clips = []

        for caption in captions:
            text_clip = self._create_text_clip(
                text=caption['text'],
                duration=caption['duration'],
                position=caption['position'],
                style=style
            )

            # Set timing
            text_clip = text_clip.set_start(caption['start_time'])

            text_clips.append(text_clip)

        # Composite all text clips with video
        final_clip = CompositeVideoClip([video_clip] + text_clips)

        return final_clip

    def _create_text_clip(self,
                         text: str,
                         duration: float,
                         position: str = "center",
                         style: str = "modern") -> TextClip:
        """
        Create a styled text clip

        Args:
            text: Text to display
            duration: Duration in seconds
            position: Position (top, center, bottom)
            style: Text style

        Returns:
            TextClip with animations
        """
        # Style settings
        style_configs = {
            'modern': {
                'fontsize': 70,
                'color': 'white',
                'font': 'Arial-Bold',
                'stroke_color': 'black',
                'stroke_width': 3
            },
            'bold': {
                'fontsize': 80,
                'color': 'yellow',
                'font': 'Impact',
                'stroke_color': 'black',
                'stroke_width': 4
            },
            'minimal': {
                'fontsize': 60,
                'color': 'white',
                'font': 'Arial',
                'stroke_color': None,
                'stroke_width': 0
            },
            'elegant': {
                'fontsize': 65,
                'color': 'white',
                'font': 'Georgia',
                'stroke_color': 'black',
                'stroke_width': 2
            }
        }

        config = style_configs.get(style, style_configs['modern'])

        # Create text clip
        txt_clip = TextClip(
            text,
            fontsize=config['fontsize'],
            color=config['color'],
            font=config['font'],
            stroke_color=config['stroke_color'],
            stroke_width=config['stroke_width'],
            method='caption',
            size=(Config.TARGET_WIDTH - 120, None),  # Padding
            align='center'
        )

        # Position
        pos = self._get_position_coords(position)
        txt_clip = txt_clip.set_position(pos)

        # Duration
        txt_clip = txt_clip.set_duration(duration)

        # Animations
        txt_clip = self._apply_animation(txt_clip, Config.TEXT_ANIMATION)

        return txt_clip

    def _get_position_coords(self, position: str) -> Tuple:
        """
        Get position coordinates for text

        Args:
            position: Position name (top, center, bottom)

        Returns:
            Position tuple for MoviePy
        """
        positions = {
            'top': ('center', 150),
            'center': ('center', 'center'),
            'bottom': ('center', Config.TARGET_HEIGHT - 200)
        }

        return positions.get(position, ('center', 'center'))

    def _apply_animation(self, clip, animation: str):
        """
        Apply animation to text clip

        Args:
            clip: TextClip to animate
            animation: Animation type (fade, slide, zoom, none)

        Returns:
            Animated clip
        """
        if animation == "fade":
            # Fade in and out
            clip = clip.crossfadein(0.3).crossfadeout(0.3)

        elif animation == "slide":
            # Slide in from bottom
            # Note: This is simplified, full implementation would use clip.set_position
            clip = clip.crossfadein(0.2).crossfadeout(0.2)

        elif animation == "zoom":
            # Zoom in effect
            # Note: This is simplified, full implementation would use clip.resize
            clip = clip.crossfadein(0.2).crossfadeout(0.2)

        # Default: just fade
        elif animation != "none":
            clip = clip.crossfadein(0.3).crossfadeout(0.3)

        return clip

    def create_title_card(self,
                         title: str,
                         duration: float = 2.0,
                         style: str = "bold") -> TextClip:
        """
        Create an opening title card

        Args:
            title: Title text
            duration: Duration to display
            style: Text style

        Returns:
            TextClip for title card
        """
        # Create large, centered title
        txt_clip = TextClip(
            title,
            fontsize=90,
            color='white',
            font='Impact',
            stroke_color='black',
            stroke_width=5,
            method='caption',
            size=(Config.TARGET_WIDTH - 80, None),
            align='center'
        )

        # Center on screen
        txt_clip = txt_clip.set_position(('center', 'center'))
        txt_clip = txt_clip.set_duration(duration)

        # Dramatic fade
        txt_clip = txt_clip.crossfadein(0.5).crossfadeout(0.5)

        return txt_clip

    def add_watermark(self,
                     video_clip,
                     watermark_text: str,
                     position: str = "bottom-right",
                     opacity: float = 0.5) -> CompositeVideoClip:
        """
        Add a watermark to the video

        Args:
            video_clip: VideoFileClip
            watermark_text: Watermark text (e.g., "@username")
            position: Position (bottom-right, bottom-left, top-right, top-left)
            opacity: Opacity (0-1)

        Returns:
            CompositeVideoClip with watermark
        """
        # Create small watermark text
        watermark = TextClip(
            watermark_text,
            fontsize=30,
            color='white',
            font='Arial',
            stroke_color='black',
            stroke_width=1
        )

        # Position
        positions = {
            'bottom-right': (Config.TARGET_WIDTH - watermark.w - 20, Config.TARGET_HEIGHT - 50),
            'bottom-left': (20, Config.TARGET_HEIGHT - 50),
            'top-right': (Config.TARGET_WIDTH - watermark.w - 20, 20),
            'top-left': (20, 20)
        }

        pos = positions.get(position, positions['bottom-right'])
        watermark = watermark.set_position(pos)

        # Set duration and opacity
        watermark = watermark.set_duration(video_clip.duration)
        watermark = watermark.set_opacity(opacity)

        # Composite
        final = CompositeVideoClip([video_clip, watermark])

        return final

    def create_progress_bar(self,
                           duration: float,
                           width: int = 800,
                           height: int = 8) -> CompositeVideoClip:
        """
        Create an animated progress bar

        Args:
            duration: Duration of the progress bar
            width: Width in pixels
            height: Height in pixels

        Returns:
            CompositeVideoClip with progress bar
        """
        # This would require more complex animation with ImageClip
        # For now, returning a placeholder
        # TODO: Implement animated progress bar
        logger.warning("Progress bar not yet implemented")
        return None
