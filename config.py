"""
Configuration settings for Media to MP3 Downloader
"""

import os

# Default directories
DEFAULT_DOWNLOAD_DIR = os.path.normpath(r"d:\code\html\music-player\NHAC")
os.makedirs(DEFAULT_DOWNLOAD_DIR, exist_ok=True)

# Audio quality options (in kbps)
AVAILABLE_QUALITIES = ["128", "192", "256", "320"]
DEFAULT_QUALITY = "320"

# Features
DEFAULT_EMBED_THUMBNAIL = True
DEFAULT_EMBED_METADATA = True

# Supported platforms hints
SUPPORTED_PLATFORMS = [
    "YouTube (Video, Shorts, Music, Playlist)",
    "TikTok (Video, Photo Slides, Âm thanh gốc)",
    "Facebook Video / Reels",
    "Instagram Reels / Videos",
    "SoundCloud",
    "Twitter / X",
]
