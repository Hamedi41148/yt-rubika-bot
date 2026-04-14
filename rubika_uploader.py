"""
آپلودر روبیکا — ارسال فایل به سیو مسیج (پیام‌های ذخیره‌شده)
نسخه بهبودیافته با رفع مشکل guid و اتصال مجدد خودکار
"""

import asyncio
import logging
from pathlib import Path

import rubpy

logger = logging.getLogger(__name__)


class RubikaUploader:
    """مدیریت اتصال و آپلود به روبیکا"""

    def __init__(self, session_name: str = "rubika_session"):
        self.session_name = session_name
        self._client = None
        self._my_guid = None   # user_guid خودمون — برای سیو مسیج

    async def connect(self) -> None:
        """اتصال به روبیکا با سشن ذخیره‌شده"""
        try:
            self._client = rubpy.Client(self.session_name)
            await self._client.__aenter__()
            me = await self._client.get_me()

            # guid درست رو پیدا میکنیم — user_guid نه user_id
            if hasattr(me, "user_guid"):
                self._my_guid = me.user_guid
            elif hasattr(me, "guid"):
                self._my_guid = me.guid
            else:
                # fallback — اگه هیچکدام نبود خطا میده
                raise AttributeError(
                    f"نتوانستیم user_guid رو پیدا کنیم. attrs موجود: {dir(me)}"
                )

            logger.info(f"✅ روبیکا متصل شد | guid={self._my_guid}")
        except Exception as e:
            self._client = None
            self._my_guid = None
            raise RuntimeError(f"خطا در اتصال به روبیکا: {e}") from e

    async def _ensure_connected(self) -> None:
        """اگه قطع شده دوباره وصل میشه"""
        if self._client is None or self._my_guid is None:
            logger.warning("روبیکا قطع بود — اتصال مجدد...")
            await self.connect()

    async def disconnect(self) -> None:
        if self._client:
            try:
                await self._client.__aexit__(None, None, None)
            except Exception:
                pass
            finally:
                self._client = None
                self._my_guid = None

    async def upload_to_saved(self, file_path: str, caption: str = "") -> None:
        """
        آپلود فایل به سیو مسیج روبیکا
        سیو مسیج = ارسال پیام به خودت (object_guid == user_guid خودت)
        """
        await self._ensure_connected()

        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"فایل پیدا نشد: {file_path}")

        size_mb = path.stat().st_size / (1024 * 1024)
        logger.info(f"آپلود شروع | {path.name} | {size_mb:.1f} MB → guid={self._my_guid}")

        ext = path.suffix.lower()

        try:
            if ext == ".mp3":
                await self._client.send_music(
                    object_guid=self._my_guid,
                    file=str(path),
                    caption=caption,
                )
            elif ext == ".mp4":
                await self._client.send_video(
                    object_guid=self._my_guid,
                    file=str(path),
                    caption=caption,
                )
            else:
                await self._client.send_document(
                    object_guid=self._my_guid,
                    file=str(path),
                    caption=caption,
                )
            logger.info(f"✅ آپلود کامل | {path.name}")

        except (AttributeError, TypeError) as e:
            # بعضی نسخه‌های rubpy متد send_video/send_music ندارن — fallback
            logger.warning(f"متد مستقیم کار نکرد ({e}) — از send_document استفاده میکنم")
            await self._client.send_document(
                object_guid=self._my_guid,
                file=str(path),
                caption=caption,
            )
            logger.info(f"✅ آپلود (document) کامل | {path.name}")

        except Exception as e:
            # اگه خطای اتصال بود، یه بار retry میکنیم
            if "connect" in str(e).lower() or "session" in str(e).lower():
                logger.warning(f"مشکل اتصال، retry... ({e})")
                self._client = None
                self._my_guid = None
                await self._ensure_connected()
                await self._client.send_document(
                    object_guid=self._my_guid,
                    file=str(path),
                    caption=caption,
                )
            else:
                raise

    @property
    def is_connected(self) -> bool:
        return self._client is not None and self._my_guid is not None

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, *args):
        await self.disconnect()
