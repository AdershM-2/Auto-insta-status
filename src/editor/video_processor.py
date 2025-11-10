"""
Core video processing engine using MoviePy and FFmpeg
"""
from pathlib import Path
from typing import List, Optional, Tuple
import numpy as np
from moviepy.editor import (
    VideoFileClip, ImageClip, CompositeVideoClip,
    concatenate_videoclips, AudioFileClip, TextClip
)
from PIL import Image

from src.utils.config import Config
from src.utils.helpers import get_logger

logger = get_logger(__name__)


class VideoProcessor:
    """
    Core video processing class that handles:
    - Video/image loading and resizing
    - Clip concatenation
    - Transitions
    - Audio integration
    - Final rendering
    """

    def __init__(self):
        self.config = Config()
        self.temp_files = []

    def load_image(self, image_path: Path, duration: float = None) -> ImageClip:
        """
        Load an image and convert to video clip

        Args:
            image_path: Path to image file
            duration: How long to display image (seconds)

        Returns:
            ImageClip object
        """
        logger.info(f"Loading image: {image_path}")

        if duration is None:
            duration = Config.DEFAULT_IMAGE_DURATION

        # Load and resize image
        img = Image.open(image_path)
        img_resized = self._smart_resize(img)

        # Convert to ImageClip
        clip = ImageClip(np.array(img_resized))
        clip = clip.set_duration(duration)
        clip = clip.set_fps(Config.TARGET_FPS)

        return clip

    def load_video(self, video_path: Path,
                   start_time: float = None,
                   end_time: float = None) -> VideoFileClip:
        """
        Load a video clip with optional trimming

        Args:
            video_path: Path to video file
            start_time: Start time in seconds
            end_time: End time in seconds

        Returns:
            VideoFileClip object
        """
        logger.info(f"Loading video: {video_path}")

        clip = VideoFileClip(str(video_path))

        # Trim if requested
        if start_time is not None or end_time is not None:
            clip = clip.subclip(start_time, end_time)

        # Resize to target dimensions
        clip = self._resize_video(clip)

        return clip

    def _smart_resize(self, img: Image.Image) -> Image.Image:
        """
        Intelligently resize and crop image to 9:16 (1080x1920)
        Tries to keep the most important content centered

        Args:
            img: PIL Image

        Returns:
            Resized PIL Image
        """
        target_w, target_h = Config.TARGET_WIDTH, Config.TARGET_HEIGHT
        target_aspect = target_h / target_w  # 16:9 = 1.777

        img_w, img_h = img.size
        img_aspect = img_h / img_w

        if img_aspect > target_aspect:
            # Image is taller than target - fit width and crop height
            new_w = target_w
            new_h = int(target_w * img_aspect)
            img_resized = img.resize((new_w, new_h), Image.Resampling.LANCZOS)

            # Crop from center
            crop_top = (new_h - target_h) // 2
            img_cropped = img_resized.crop((0, crop_top, target_w, crop_top + target_h))
        else:
            # Image is wider than target - fit height and crop width
            new_h = target_h
            new_w = int(target_h / img_aspect)
            img_resized = img.resize((new_w, new_h), Image.Resampling.LANCZOS)

            # Crop from center
            crop_left = (new_w - target_w) // 2
            img_cropped = img_resized.crop((crop_left, 0, crop_left + target_w, target_h))

        return img_cropped

    def _resize_video(self, clip: VideoFileClip) -> VideoFileClip:
        """
        Resize video clip to target dimensions (1080x1920)

        Args:
            clip: VideoFileClip to resize

        Returns:
            Resized VideoFileClip
        """
        target_w, target_h = Config.TARGET_WIDTH, Config.TARGET_HEIGHT
        target_aspect = target_h / target_w

        clip_aspect = clip.h / clip.w

        if clip_aspect > target_aspect:
            # Video is taller - fit width and crop height
            clip_resized = clip.resize(width=target_w)
            # Crop vertically from center
            y_center = clip_resized.h / 2
            clip_cropped = clip_resized.crop(
                y1=int(y_center - target_h / 2),
                y2=int(y_center + target_h / 2)
            )
        else:
            # Video is wider - fit height and crop width
            clip_resized = clip.resize(height=target_h)
            # Crop horizontally from center
            x_center = clip_resized.w / 2
            clip_cropped = clip_resized.crop(
                x1=int(x_center - target_w / 2),
                x2=int(x_center + target_w / 2)
            )

        return clip_cropped

    def apply_transition(self, clip1, clip2, transition_type: str = "fade",
                        duration: float = None) -> List:
        """
        Apply transition between two clips

        Args:
            clip1: First clip
            clip2: Second clip
            transition_type: Type of transition (fade, slide, zoom)
            duration: Transition duration in seconds

        Returns:
            List of clips with transition applied
        """
        if duration is None:
            duration = Config.TRANSITION_DURATION

        if transition_type == "fade":
            # Crossfade between clips
            clip1 = clip1.crossfadeout(duration)
            clip2 = clip2.crossfadein(duration)
            return [clip1, clip2]

        elif transition_type == "slide":
            # Slide transition (simplified)
            # TODO: Implement proper slide animation
            return [clip1, clip2]

        elif transition_type == "zoom":
            # Zoom transition (simplified)
            # TODO: Implement zoom animation
            return [clip1, clip2]

        else:
            # No transition, just concatenate
            return [clip1, clip2]

    def concatenate_clips(self, clips: List, method: str = "compose") -> VideoFileClip:
        """
        Concatenate multiple clips into one

        Args:
            clips: List of VideoFileClip or ImageClip objects
            method: 'compose' for crossfade, 'chain' for direct concatenation

        Returns:
            Single concatenated VideoFileClip
        """
        logger.info(f"Concatenating {len(clips)} clips")

        if method == "compose":
            # Use compose for smooth transitions
            final_clip = concatenate_videoclips(clips, method="compose")
        else:
            # Direct concatenation
            final_clip = concatenate_videoclips(clips, method="chain")

        return final_clip

    def add_audio(self, video_clip, audio_path: Path,
                  fade_in: float = None,
                  fade_out: float = None) -> VideoFileClip:
        """
        Add background music to video

        Args:
            video_clip: VideoFileClip to add audio to
            audio_path: Path to audio file
            fade_in: Fade in duration (seconds)
            fade_out: Fade out duration (seconds)

        Returns:
            VideoFileClip with audio
        """
        logger.info(f"Adding audio: {audio_path}")

        if fade_in is None:
            fade_in = Config.MUSIC_FADE_IN
        if fade_out is None:
            fade_out = Config.MUSIC_FADE_OUT

        audio = AudioFileClip(str(audio_path))

        # Trim or loop audio to match video duration
        if audio.duration < video_clip.duration:
            # Loop audio
            repeats = int(video_clip.duration / audio.duration) + 1
            audio = audio.loop(repeats)

        # Trim to video length
        audio = audio.subclip(0, video_clip.duration)

        # Apply fades
        if fade_in > 0:
            audio = audio.audio_fadein(fade_in)
        if fade_out > 0:
            audio = audio.audio_fadeout(fade_out)

        # Set audio to video
        video_with_audio = video_clip.set_audio(audio)

        return video_with_audio

    def add_text_overlay(self, video_clip, text: str,
                        position: str = "center",
                        start_time: float = 0,
                        duration: float = None,
                        font_size: int = None) -> CompositeVideoClip:
        """
        Add text overlay to video

        Args:
            video_clip: VideoFileClip to add text to
            text: Text to display
            position: Position ('top', 'center', 'bottom')
            start_time: When text appears (seconds)
            duration: How long text displays (seconds)
            font_size: Font size

        Returns:
            CompositeVideoClip with text
        """
        if duration is None:
            duration = Config.TEXT_DURATION
        if font_size is None:
            font_size = Config.TEXT_FONT_SIZE

        # Position mapping
        position_map = {
            'top': ('center', 100),
            'center': ('center', 'center'),
            'bottom': ('center', video_clip.h - 150)
        }

        pos = position_map.get(position, ('center', 'center'))

        # Create text clip with white text and black stroke
        txt_clip = TextClip(
            text,
            fontsize=font_size,
            color='white',
            stroke_color='black',
            stroke_width=2,
            font='Arial-Bold',
            method='caption',
            size=(Config.TARGET_WIDTH - 100, None)  # Add padding
        )

        # Set timing and position
        txt_clip = txt_clip.set_position(pos)
        txt_clip = txt_clip.set_start(start_time)
        txt_clip = txt_clip.set_duration(duration)

        # Apply fade in/out
        txt_clip = txt_clip.crossfadein(0.3).crossfadeout(0.3)

        # Composite with video
        video_with_text = CompositeVideoClip([video_clip, txt_clip])

        return video_with_text

    def render(self, video_clip, output_path: Path,
              preset: str = "medium") -> Path:
        """
        Render final video to file

        Args:
            video_clip: VideoFileClip to render
            output_path: Output file path
            preset: Encoding preset (ultrafast, fast, medium, slow)

        Returns:
            Path to rendered video
        """
        logger.info(f"Rendering video to: {output_path}")

        output_path.parent.mkdir(parents=True, exist_ok=True)

        video_clip.write_videofile(
            str(output_path),
            codec=Config.VIDEO_CODEC,
            audio_codec=Config.AUDIO_CODEC,
            bitrate=Config.VIDEO_BITRATE,
            fps=Config.TARGET_FPS,
            preset=preset,
            threads=4
        )

        logger.info(f"✓ Video rendered successfully: {output_path}")
        return output_path

    def cleanup(self):
        """Clean up temporary files"""
        for temp_file in self.temp_files:
            if temp_file.exists():
                temp_file.unlink()
        self.temp_files.clear()
