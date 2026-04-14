"""
تنظیمات مرکزی — تمام مقادیر هاردکد شده‌اند
"""


class Config:
    # ── توکن بات تلگرام ───────────────────────────────────────────────────────
    TELEGRAM_BOT_TOKEN: str = "6552413876:AAERNZGLwq7DYAAoGlQj-Jbqyn9C-cA5Egg"

    # ── ادمین‌های مجاز — فقط این آیدی می‌تونه از بات استفاده کنه ─────────────
    ADMIN_IDS: set = {5485182134}

    # ── روبیکا ────────────────────────────────────────────────────────────────
    RUBIKA_SESSION: str = "rubika_session"
    RUBIKA_PHONE: str = "+989046056562"

    # ── دانلود ────────────────────────────────────────────────────────────────
    DOWNLOAD_PATH: str = "./downloads"
    MAX_FILE_SIZE_MB: int = 2048

    @classmethod
    def validate(cls) -> None:
        if not cls.TELEGRAM_BOT_TOKEN:
            raise EnvironmentError("❌ TELEGRAM_BOT_TOKEN خالیه!")
