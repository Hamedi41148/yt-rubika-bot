"""
دانلودر یوتیوب با yt-dlp — نسخه بهبودیافته با رفع خطاهای SSL و فرمت
"""

import asyncio
import logging
import os
import subprocess
import sys
import uuid
from pathlib import Path

import yt_dlp

logger = logging.getLogger(__name__)


def auto_update_ytdlp():
    """آپدیت خودکار yt-dlp — هر بار که بات استارت میشه"""
    try:
        logger.info("⏫ بررسی آپدیت yt-dlp...")
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "--upgrade", "yt-dlp", "-q"],
            capture_output=True,
            timeout=60,
        )
        if result.returncode == 0:
            logger.info("✅ yt-dlp آپدیت شد / آخرین نسخه است")
        else:
            logger.warning(f"⚠️ آپدیت ناموفق: {result.stderr.decode()[:200]}")
    except Exception as e:
        logger.warning(f"⚠️ نتوانستیم yt-dlp را آپدیت کنیم: {e}")


class YouTubeDownloader:
    """دانلودر بهینه یوتیوب با رفع تمام خطاهای رایج"""

    # فرمت‌ها با fallback کامل — رفع خطای "format not available"
    FORMAT_MAP = {
        "1080": (
            "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]"
            "/bestvideo[height<=1080][ext=mp4]+bestaudio"
            "/bestvideo[height<=1080]+bestaudio[ext=m4a]"
            "/bestvideo[height<=1080]+bestaudio"
            "/best[height<=1080][ext=mp4]/best[height<=1080]/best[ext=mp4]/best"
        ),
        "720": (
            "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]"
            "/bestvideo[height<=720][ext=mp4]+bestaudio"
            "/bestvideo[height<=720]+bestaudio[ext=m4a]"
            "/bestvideo[height<=720]+bestaudio"
            "/best[height<=720][ext=mp4]/best[height<=720]/best[ext=mp4]/best"
        ),
        "480": (
            "bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]"
            "/bestvideo[height<=480][ext=mp4]+bestaudio"
            "/bestvideo[height<=480]+bestaudio"
            "/best[height<=480][ext=mp4]/best[height<=480]/best[ext=mp4]/best"
        ),
        "audio": (
            "bestaudio[ext=m4a]/bestaudio[ext=mp3]/bestaudio[ext=webm]/bestaudio"
        ),
    }

    def __init__(self, download_path: str):
        self.download_path = Path(download_path)
        self.download_path.mkdir(parents=True, exist_ok=True)

    def _common_opts(self) -> dict:
        """تنظیمات مشترک — شامل رفع SSL و هدر مرورگر"""
        return {
            "noplaylist": True,
            "quiet": True,
            "no_warnings": True,
            "retries": 10,
            "fragment_retries": 10,
            "extractor_retries": 5,
            "file_access_retries": 5,
            "concurrent_fragment_downloads": 3,
            # ── رفع خطای SSL ────────────────────────────
            "nocheckcertificate": True,
            "socket_timeout": 30,
            "source_address": "0.0.0.0",
            # ── هدر مرورگر ──────────────────────────────
            "http_headers": {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/124.0.0.0 Safari/537.36"
                ),
                "Accept-Language": "en-US,en;q=0.9",
            },
        }

    def _build_opts(self, quality: str, output_template: str) -> dict:
        is_audio = quality == "audio"
        opts = self._common_opts()
        opts.update({
            "format": self.FORMAT_MAP.get(quality, self.FORMAT_MAP["720"]),
            "outtmpl": output_template,
            "merge_output_format": "mp3" if is_audio else "mp4",
            "postprocessors": [],
        })
        if is_audio:
            opts["postprocessors"].append({
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            })
        else:
            opts["postprocessors"].append({"key": "FFmpegMetadata"})
        return opts

    async def get_info(self, url: str) -> dict:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._get_info_sync, url)

    def _get_info_sync(self, url: str) -> dict:
        opts = self._common_opts()
        with yt_dlp.YoutubeDL(opts) as ydl:
            return ydl.extract_info(url, download=False)

    async def download(self, url: str, quality: str) -> str:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._download_sync, url, quality)

    def _download_sync(self, url: str, quality: str) -> str:
        uid = uuid.uuid4().hex[:8]
        ext = "mp3" if quality == "audio" else "mp4"
        output_template = str(self.download_path / f"{uid}.%(ext)s")
        expected_path = str(self.download_path / f"{uid}.{ext}")

        opts = self._build_opts(quality, output_template)
        logger.info(f"دانلود شروع شد | quality={quality} | url={url}")

        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.download([url])

        # پیدا کردن فایل — پسوند ممکنه فرق داشته باشه
        if os.path.exists(expected_path):
            return expected_path

        for f in sorted(self.download_path.iterdir(),
                        key=lambda x: x.stat().st_mtime, reverse=True):
            if f.stem == uid:
                logger.info(f"فایل با پسوند {f.suffix} پیدا شد")
                return str(f)

        raise FileNotFoundError(
            "❌ فایل دانلودشده پیدا نشد.\n"
            "احتمالاً فرمت درخواستی موجود نیست یا دانلود ناقص بود.\n"
            "کیفیت پایین‌تر رو امتحان کن."
        )
