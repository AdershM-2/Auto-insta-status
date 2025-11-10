#!/usr/bin/env python3
"""
Auto Instagram Status - AI-Powered Reel Editor
Main CLI entry point
"""
import argparse
import sys
from pathlib import Path
from typing import List
import time

from src.utils.config import Config
from src.utils.helpers import get_logger, parse_file_list, validate_media_files
from src.editor.video_processor import VideoProcessor
from src.editor.clip_selector import ClipSelector
from src.analyzer import MomentScorer
from src.text import CaptionGenerator, TextOverlayManager
from src.audio import AudioSynchronizer

logger = get_logger(__name__)


class ReelEditor:
    """
    Main reel editor orchestrator
    """

    def __init__(self):
        self.processor = VideoProcessor()
        self.clip_selector = ClipSelector()
        self.caption_generator = CaptionGenerator(use_ollama=True)
        self.text_manager = TextOverlayManager()
        self.audio_sync = AudioSynchronizer()

    def create_reel(self,
                    images: List[Path],
                    videos: List[Path],
                    description: str,
                    output_path: Path,
                    music_path: Path = None,
                    duration: int = 30,
                    style: str = "engaging") -> Path:
        """
        Create an Instagram reel from images and videos

        Args:
            images: List of image paths
            videos: List of video paths
            description: User description of the content
            output_path: Output file path
            music_path: Optional background music path
            duration: Target duration in seconds
            style: Style (engaging, professional, fun, minimal)

        Returns:
            Path to created reel
        """
        logger.info("=" * 60)
        logger.info("🎬 Starting AI Reel Creation")
        logger.info("=" * 60)

        start_time = time.time()

        # Validate inputs
        if not images and not videos:
            logger.error("No media files provided!")
            sys.exit(1)

        if not validate_media_files(images, videos):
            logger.error("Invalid media files")
            sys.exit(1)

        # Step 1: Select best clips
        logger.info("\n📊 Step 1/5: Analyzing and selecting best clips...")
        selected_clips = self.clip_selector.select_clips(
            images=images,
            videos=videos,
            target_duration=duration,
            description=description
        )

        if not selected_clips:
            logger.error("No clips selected!")
            sys.exit(1)

        # Step 2: Generate captions
        logger.info("\n✍️  Step 2/5: Generating AI captions...")
        clip_durations = [clip.duration for clip in selected_clips]

        captions = self.caption_generator.generate_captions(
            description=description,
            num_clips=len(selected_clips),
            clip_durations=clip_durations,
            style=style
        )

        # Step 3: Sync to music (if provided)
        if music_path and music_path.exists():
            logger.info("\n🎵 Step 3/5: Synchronizing to music beats...")
            synced_clips = self.audio_sync.sync_clips_to_music(
                clip_durations=clip_durations,
                audio_path=music_path,
                target_duration=duration
            )

            # Update clip durations based on sync
            for i, synced in enumerate(synced_clips):
                if i < len(selected_clips):
                    selected_clips[i].duration = synced.duration
        else:
            logger.info("\n⏭️  Step 3/5: Skipping music sync (no music provided)")

        # Step 4: Create video clips
        logger.info("\n🎞️  Step 4/5: Processing and combining clips...")
        video_clips = []

        for i, selected in enumerate(selected_clips):
            logger.info(f"Processing clip {i+1}/{len(selected_clips)}: {selected.source_path.name}")

            if selected.clip_type == 'image':
                clip = self.processor.load_image(
                    selected.source_path,
                    duration=selected.duration
                )
            else:  # video
                clip = self.processor.load_video(
                    selected.source_path,
                    start_time=selected.start_time,
                    end_time=selected.end_time
                )

            video_clips.append(clip)

        # Concatenate all clips
        logger.info("Concatenating clips...")
        final_video = self.processor.concatenate_clips(video_clips, method="compose")

        # Step 5: Add text overlays
        logger.info("\n📝 Step 5/5: Adding text overlays...")
        final_video = self.text_manager.add_captions_to_video(
            final_video,
            captions=captions,
            style="modern"
        )

        # Add background music
        if music_path and music_path.exists():
            logger.info("Adding background music...")
            final_video = self.processor.add_audio(
                final_video,
                audio_path=music_path
            )

        # Render final video
        logger.info("\n🎬 Rendering final video...")
        output_path = self.processor.render(final_video, output_path, preset="medium")

        # Cleanup
        logger.info("\n🧹 Cleaning up...")
        self.processor.cleanup()
        self.clip_selector.close()

        elapsed = time.time() - start_time
        logger.info("=" * 60)
        logger.info(f"✅ Reel created successfully in {elapsed:.1f}s")
        logger.info(f"📍 Output: {output_path}")
        logger.info("=" * 60)

        return output_path


def main():
    """CLI entry point"""

    parser = argparse.ArgumentParser(
        description="Auto Instagram Status - AI-Powered Reel Editor",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage with images
  python main.py --images "img1.jpg,img2.jpg,img3.jpg" --description "Beach day"

  # With videos and music
  python main.py \\
    --images "*.jpg" \\
    --videos "clip1.mp4,clip2.mp4" \\
    --music "song.mp3" \\
    --description "Epic mountain adventure" \\
    --duration 30

  # Custom output path and style
  python main.py \\
    --images "photos/*.jpg" \\
    --description "Product showcase" \\
    --output "output/product_reel.mp4" \\
    --style "professional" \\
    --duration 15
        """
    )

    parser.add_argument(
        '--images',
        type=str,
        help='Comma-separated image paths or glob pattern (e.g., "img1.jpg,img2.jpg" or "*.jpg")'
    )

    parser.add_argument(
        '--videos',
        type=str,
        help='Comma-separated video paths or glob pattern'
    )

    parser.add_argument(
        '--description',
        type=str,
        required=True,
        help='Description of the reel content (used for AI caption generation)'
    )

    parser.add_argument(
        '--music',
        type=str,
        help='Path to background music file'
    )

    parser.add_argument(
        '--output',
        type=str,
        default='output/reel.mp4',
        help='Output file path (default: output/reel.mp4)'
    )

    parser.add_argument(
        '--duration',
        type=int,
        default=30,
        help='Target duration in seconds (default: 30)'
    )

    parser.add_argument(
        '--style',
        type=str,
        choices=['engaging', 'professional', 'fun', 'minimal'],
        default='engaging',
        help='Reel style (default: engaging)'
    )

    parser.add_argument(
        '--no-captions',
        action='store_true',
        help='Disable AI-generated captions'
    )

    parser.add_argument(
        '--use-openai',
        action='store_true',
        help='Use OpenAI API instead of local Ollama for captions'
    )

    args = parser.parse_args()

    # Parse file lists
    images = parse_file_list(args.images) if args.images else []
    videos = parse_file_list(args.videos) if args.videos else []

    if not images and not videos:
        logger.error("❌ No media files provided! Use --images and/or --videos")
        parser.print_help()
        sys.exit(1)

    logger.info(f"Found {len(images)} images and {len(videos)} videos")

    # Parse music path
    music_path = Path(args.music) if args.music else None

    if music_path and not music_path.exists():
        logger.warning(f"⚠️  Music file not found: {music_path}")
        music_path = None

    # Parse output path
    output_path = Path(args.output)

    # Test LLM connection
    if not args.no_captions:
        logger.info("🔍 Testing LLM connection...")
        caption_gen = CaptionGenerator(use_ollama=not args.use_openai)
        if caption_gen.test_connection():
            logger.info("✓ LLM ready")
        else:
            logger.warning("⚠️  LLM not available, will use fallback captions")

    # Create reel
    editor = ReelEditor()

    try:
        result = editor.create_reel(
            images=images,
            videos=videos,
            description=args.description,
            output_path=output_path,
            music_path=music_path,
            duration=args.duration,
            style=args.style
        )

        logger.info(f"\n🎉 Success! Your reel is ready: {result}")

    except KeyboardInterrupt:
        logger.info("\n\n⚠️  Interrupted by user")
        sys.exit(1)

    except Exception as e:
        logger.error(f"\n❌ Error creating reel: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
