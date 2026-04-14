"""
دانلودر یوتیوب با yt-dlp — پشتیبانی از کیفیت‌های مختلف و دانلود MP3
"""

import asyncio
import logging
import os
import uuid
from pathlib import Path

import yt_dlp

logger = logging.getLogger(__name__)


class YouTubeDownloader:
    """دانلودر بهینه یوتیوب"""

    FORMAT_MAP = {
        "1080": "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=1080]+bestaudio/best[height<=1080]/best",
        "720":  "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=720]+bestaudio/best[height<=720]/best",
        "480":  "bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=480]+bestaudio/best[height<=480]/best",
        "audio": "bestaudio[ext=m4a]/bestaudio",
    }

    def __init__(self, download_path: str):
        self.download_path = Path(download_path)
        self.download_path.mkdir(parents=True, exist_ok=True)

    def _build_opts(self, quality: str, output_template: str) -> dict:
        is_audio = quality == "audio"

        opts = {
            "format": self.FORMAT_MAP.get(quality, self.FORMAT_MAP["720"]),
            "outtmpl": output_template,
            "merge_output_format": "mp3" if is_audio else "mp4",
            "noplaylist": True,
            "quiet": True,
            "no_warnings": True,
            "retries": 5,
            "fragment_retries": 5,
            "concurrent_fragment_downloads": 4,
            "http_headers": {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/122.0.0.0 Safari/537.36"
                )
            },
            "postprocessors": [],
        }

        if is_audio:
            opts["postprocessors"].append(
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }
            )
        else:
            opts["postprocessors"].extend(
                [
                    {"key": "FFmpegMetadata"},
                ]
            )

        return opts

    async def get_info(self, url: str) -> dict:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._get_info_sync, url)

    def _get_info_sync(self, url: str) -> dict:
        opts = {"quiet": True, "no_warnings": True, "noplaylist": True}
        with yt_dlp.YoutubeDL(opts) as ydl:
            return ydl.extract_info(url, download=False)

    async def download(self, url: str, quality: str) -> str:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._download_sync, url, quality)

    def _download_sync(self, url: str, quality: str) -> str:
        uid = uuid.uuid4().hex[:8]
        ext = "mp3" if quality == "audio" else "mp4"
        output_template = str(self.download_path / f"{uid}.%(ext)s")
        final_path = str(self.download_path / f"{uid}.{ext}")

        opts = self._build_opts(quality, output_template)

        logger.info(f"دانلود شروع شد | quality={quality} | url={url}")
        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.download([url])

        if not os.path.exists(final_path):
            for f in self.download_path.iterdir():
                if f.stem == uid:
                    final_path = str(f)
                    break

        if not os.path.exists(final_path):
            raise FileNotFoundError(f"فایل دانلود‌شده پیدا نشد: {final_path}")

        size_mb = os.path.getsize(final_path) / (1024 * 1024)
        logger.info(f"دانلود کامل شد | {size_mb:.1f} MB | {final_path}")
        return final_path
