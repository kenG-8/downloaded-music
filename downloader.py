"""
Core Downloader module for YouTube & TikTok to MP3 320kbps
"""

import os
import sys
import time
import shutil
from typing import Optional, Callable, Dict, Any, List

# Ensure UTF-8 output on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import static_ffmpeg
# Initialize static ffmpeg binaries into PATH
static_ffmpeg.add_paths()

import yt_dlp


def format_duration(seconds: Optional[int]) -> str:
    """Format duration in seconds to hh:mm:ss or mm:ss"""
    if seconds is None:
        return "N/A"
    seconds = int(seconds)
    hours, remainder = divmod(seconds, 3600)
    minutes, sec = divmod(remainder, 60)
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{sec:02d}"
    return f"{minutes:02d}:{sec:02d}"


def format_bytes(bytes_count: Optional[float]) -> str:
    """Format bytes count to human readable string (KB, MB, GB)"""
    if bytes_count is None or bytes_count <= 0:
        return "N/A"
    for unit in ["B", "KB", "MB", "GB"]:
        if bytes_count < 1024.0:
            return f"{bytes_count:.2f} {unit}"
        bytes_count /= 1024.0
    return f"{bytes_count:.2f} TB"


from config import DEFAULT_DOWNLOAD_DIR


class MediaDownloader:
    """High quality Media to MP3 Downloader supporting YouTube, TikTok and more"""

    def __init__(
        self,
        output_dir: str = DEFAULT_DOWNLOAD_DIR,
        quality: str = "320",
        embed_thumbnail: bool = True,
        on_progress: Optional[Callable[[Dict[str, Any]], None]] = None,
        on_status: Optional[Callable[[str], None]] = None,
    ):
        self.output_dir = os.path.abspath(output_dir)
        self.quality = quality
        self.embed_thumbnail = embed_thumbnail
        self.on_progress = on_progress
        self.on_status = on_status

        os.makedirs(self.output_dir, exist_ok=True)

    def _progress_hook(self, d: Dict[str, Any]):
        status = d.get("status")
        if status == "downloading":
            downloaded = d.get("downloaded_bytes", 0)
            total = d.get("total_bytes") or d.get("total_bytes_estimate", 0)
            speed = d.get("speed")
            eta = d.get("eta")

            percent = (downloaded / total * 100) if total > 0 else 0

            if self.on_progress:
                self.on_progress({
                    "status": "downloading",
                    "downloaded": downloaded,
                    "total": total,
                    "percent": percent,
                    "speed": speed,
                    "eta": eta,
                    "filename": d.get("filename", ""),
                })
        elif status == "finished":
            if self.on_status:
                self.on_status("Đang chuyển đổi sang định dạng MP3 320kbps...")

    def _postprocessor_hook(self, d: Dict[str, Any]):
        pp = d.get("postprocessor", "")
        status = d.get("status", "")
        if self.on_status:
            if pp == "ExtractAudio" and status == "started":
                self.on_status("Đang giải mã và trích xuất âm thanh...")
            elif pp == "EmbedThumbnail" and status == "started":
                self.on_status("Đang nhúng ảnh bìa chất lượng cao vào file MP3...")
            elif pp == "Metadata" and status == "started":
                self.on_status("Đang ghi thông tin bài hát (ID3 tags)...")

    def get_info(self, url: str) -> Dict[str, Any]:
        """Fetch video information without downloading"""
        opts = {
            "quiet": True,
            "no_warnings": True,
            "skip_download": True,
            "js_runtimes": {"node": {}},
        }
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if "_type" in info and info["_type"] == "playlist":
                # For playlists, take playlist metadata or entries
                entries = list(info.get("entries", []))
                return {
                    "is_playlist": True,
                    "title": info.get("title", "Danh sách phát"),
                    "uploader": info.get("uploader", "N/A"),
                    "count": len(entries),
                    "entries": entries,
                    "extractor": info.get("extractor_key", "Playlist"),
                }

            return {
                "is_playlist": False,
                "title": info.get("title", "Không có tiêu đề"),
                "uploader": info.get("uploader") or info.get("channel") or info.get("creator") or "N/A",
                "duration": info.get("duration"),
                "formatted_duration": format_duration(info.get("duration")),
                "thumbnail": info.get("thumbnail"),
                "view_count": info.get("view_count"),
                "extractor": info.get("extractor_key", "N/A"),
                "url": url,
            }

    def download(self, url: str) -> Dict[str, Any]:
        """Download and convert media to MP3 320kbps"""
        start_time = time.time()

        # Build postprocessors
        postprocessors: List[Dict[str, Any]] = [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": str(self.quality),
            },
        ]

        if self.embed_thumbnail:
            postprocessors.extend([
                {
                    "key": "FFmpegThumbnailsConvertor",
                    "format": "jpg",
                },
                {
                    "key": "EmbedThumbnail",
                    "already_have_thumbnail": False,
                },
            ])

        postprocessors.append({
            "key": "FFmpegMetadata",
            "add_metadata": True,
        })

        outtmpl = os.path.join(self.output_dir, "%(title)s.%(ext)s")

        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": outtmpl,
            "windowsfilenames": True,
            "js_runtimes": {"node": {}},
            "postprocessors": postprocessors,
            "writethumbnail": self.embed_thumbnail,
            "quiet": True,
            "no_warnings": True,
            "progress_hooks": [self._progress_hook],
            "postprocessor_hooks": [self._postprocessor_hook],
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Extract info and download
            info = ydl.extract_info(url, download=True)
            elapsed = time.time() - start_time

            # Handle playlist vs single
            if "_type" in info and info["_type"] == "playlist":
                return {
                    "is_playlist": True,
                    "title": info.get("title", "Playlist"),
                    "count": len(list(info.get("entries", []))),
                    "output_dir": self.output_dir,
                    "elapsed": elapsed,
                }

            # Expected MP3 file path
            expected_title = ydl.prepare_filename(info)
            base, _ = os.path.splitext(expected_title)
            final_mp3_path = f"{base}.mp3"

            file_size = 0
            if os.path.exists(final_mp3_path):
                file_size = os.path.getsize(final_mp3_path)

            return {
                "is_playlist": False,
                "title": info.get("title", "Audio"),
                "uploader": info.get("uploader") or info.get("channel") or "N/A",
                "duration": info.get("duration"),
                "formatted_duration": format_duration(info.get("duration")),
                "file_path": final_mp3_path,
                "file_name": os.path.basename(final_mp3_path),
                "file_size": file_size,
                "formatted_size": format_bytes(file_size),
                "quality": f"{self.quality} kbps",
                "elapsed": elapsed,
            }
