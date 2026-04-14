"""
آپلودر روبیکا — ارسال فایل به سیو مسیج (پیام‌های ذخیره‌شده)
"""

import asyncio
import logging
import os
from pathlib import Path

import rubpy

logger = logging.getLogger(__name__)


class RubikaUploader:
    """مدیریت اتصال و آپلود به روبیکا"""

    def __init__(self, session_name: str = "rubika_session"):
        self.session_name = session_name
        self._client = None
        self._me = None

    async def connect(self) -> None:
        """اتصال به روبیکا با استفاده از سشن ذخیره‌شده"""
        self._client = rubpy.Client(self.session_name)
        await self._client.__aenter__()
        self._me = await self._client.get_me()
        logger.info(f"روبیکا: وارد شدیم — user_id={self._me.user_id}")

    async def disconnect(self) -> None:
        if self._client:
            try:
                await self._client.__aexit__(None, None, None)
            except Exception:
                pass
            self._client = None
            self._me = None

    async def upload_to_saved(self, file_path: str, caption: str = "") -> None:
        """
        آپلود فایل به سیو مسیج روبیکا
        سیو مسیج = ارسال پیام به خودت (object_guid == user_guid خودت)
        """
        if not self._client or not self._me:
            raise RuntimeError("روبیکا متصل نیست — ابتدا connect() رو صدا بزن")

        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"فایل پیدا نشد: {file_path}")

        file_size_mb = file_path.stat().st_size / (1024 * 1024)
        logger.info(f"آپلود شروع شد | {file_path.name} | {file_size_mb:.1f} MB")

        ext = file_path.suffix.lower()
        my_guid = self._me.user_id  # سیو مسیج = ارسال به خودت

        try:
            if ext == ".mp3":
                await self._client.send_music(
                    object_guid=my_guid,
                    file=str(file_path),
                    caption=caption,
                )
            elif ext == ".mp4":
                await self._client.send_video(
                    object_guid=my_guid,
                    file=str(file_path),
                    caption=caption,
                )
            else:
                await self._client.send_document(
                    object_guid=my_guid,
                    file=str(file_path),
                    caption=caption,
                )

            logger.info(f"آپلود کامل شد | {file_path.name}")

        except AttributeError as e:
            logger.warning(f"متد مستقیم نبود، از send_document استفاده می‌کنم: {e}")
            await self._client.send_document(
                object_guid=my_guid,
                file=str(file_path),
                caption=caption,
            )

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, *args):
        await self.disconnect()
