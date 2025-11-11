"""
Interactive mode for easy reel creation
"""
import os
from pathlib import Path
from typing import List, Tuple
import sys

from src.utils.helpers import get_logger

logger = get_logger(__name__)


def get_media_from_folder(folder_path: str) -> Tuple[List[Path], List[Path]]:
    """
    Automatically find all images and videos in a folder

    Args:
        folder_path: Path to folder

    Returns:
        Tuple of (images, videos)
    """
    folder = Path(folder_path)

    if not folder.exists() or not folder.is_dir():
        logger.error(f"Folder not found: {folder_path}")
        return [], []

    # Image extensions
    image_exts = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
    # Video extensions
    video_exts = {'.mp4', '.mov', '.avi', '.mkv', '.webm', '.flv', '.wmv'}

    images = []
    videos = []

    for file in folder.iterdir():
        if file.is_file():
            ext = file.suffix.lower()
            if ext in image_exts:
                images.append(file)
            elif ext in video_exts:
                videos.append(file)

    # Sort by name
    images.sort()
    videos.sort()

    logger.info(f"Found {len(images)} images and {len(videos)} videos in {folder_path}")

    return images, videos


def interactive_mode():
    """
    Interactive mode - prompts user for inputs
    """
    print("\n" + "=" * 60)
    print("  AI-Powered Reel Creator - Interactive Mode")
    print("=" * 60 + "\n")

    # Method selection
    print("How do you want to add media?")
    print("1. Point to a folder (easiest)")
    print("2. Enter file paths manually")
    print("3. Use current folder")
    print()

    choice = input("Enter choice (1-3) [1]: ").strip() or "1"

    images = []
    videos = []

    if choice == "1":
        # Folder mode
        folder = input("\nEnter folder path (or drag folder here): ").strip().strip('"')
        if not folder:
            print("❌ No folder specified")
            sys.exit(1)

        images, videos = get_media_from_folder(folder)

        if not images and not videos:
            print("❌ No media files found in folder")
            sys.exit(1)

        print(f"\n✓ Found:")
        print(f"  - {len(images)} images")
        print(f"  - {len(videos)} videos")

    elif choice == "2":
        # Manual entry
        print("\nEnter image paths (comma-separated, or press Enter to skip):")
        image_input = input("Images: ").strip()
        if image_input:
            images = [Path(p.strip().strip('"')) for p in image_input.split(',')]

        print("\nEnter video paths (comma-separated, or press Enter to skip):")
        video_input = input("Videos: ").strip()
        if video_input:
            videos = [Path(p.strip().strip('"')) for p in video_input.split(',')]

        if not images and not videos:
            print("❌ No media files specified")
            sys.exit(1)

    elif choice == "3":
        # Current folder
        print("\nScanning current folder...")
        images, videos = get_media_from_folder(".")

        if not images and not videos:
            print("❌ No media files found in current folder")
            sys.exit(1)

        print(f"\n✓ Found:")
        print(f"  - {len(images)} images")
        print(f"  - {len(videos)} videos")

    else:
        print("❌ Invalid choice")
        sys.exit(1)

    # Get description
    print("\n" + "-" * 60)
    print("Describe your reel (this helps AI generate better captions):")
    print("Example: 'Amazing beach vacation with friends, sunset views, and fun activities'")
    print()
    description = input("Description: ").strip()

    if not description:
        print("❌ Description is required")
        sys.exit(1)

    # Optional: Music
    print("\n" + "-" * 60)
    music_input = input("Music file (optional, press Enter to skip): ").strip().strip('"')
    music = Path(music_input) if music_input else None

    # Optional: Duration
    print("\n" + "-" * 60)
    duration_input = input("Duration in seconds (default: 30): ").strip()
    duration = int(duration_input) if duration_input else 30

    # Optional: Style
    print("\n" + "-" * 60)
    print("Style options: engaging (default), professional, fun, minimal")
    style_input = input("Style: ").strip() or "engaging"

    # Optional: Output
    print("\n" + "-" * 60)
    output_input = input("Output filename (default: output/reel.mp4): ").strip()
    output = Path(output_input) if output_input else Path("output/reel.mp4")

    # Confirm
    print("\n" + "=" * 60)
    print("Ready to create reel with:")
    print(f"  - {len(images)} images")
    print(f"  - {len(videos)} videos")
    if music:
        print(f"  - Music: {music.name}")
    print(f"  - Duration: {duration}s")
    print(f"  - Style: {style_input}")
    print(f"  - Output: {output}")
    print("=" * 60 + "\n")

    confirm = input("Create reel? (Y/n): ").strip().lower()
    if confirm and confirm != 'y':
        print("❌ Cancelled")
        sys.exit(0)

    return {
        'images': images,
        'videos': videos,
        'description': description,
        'music': music,
        'duration': duration,
        'style': style_input,
        'output': output
    }
