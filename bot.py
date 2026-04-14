#!/usr/bin/env python3
"""
YouTube → Rubika Bot — فقط ادمین مجاز است
"""

import logging
import os
import re
from pathlib import Path

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters,
)

from config import Config
from downloader import YouTubeDownloader
from rubika_uploader import RubikaUploader

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("bot.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger(__name__)

YT_PATTERN = re.compile(
    r"(https?://)?(www\.)?"
    r"(youtube\.com/(watch\?v=|shorts/|embed/)|youtu\.be/)"
    r"[\w\-]{11}"
)

downloader = YouTubeDownloader(Config.DOWNLOAD_PATH)
rubika = RubikaUploader(Config.RUBIKA_SESSION)


# ── Guard: فقط ادمین ──────────────────────────────────────────────────────────
def admin_only(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        uid = update.effective_user.id if update.effective_user else None
        if uid not in Config.ADMIN_IDS:
            await update.effective_message.reply_text("⛔ دسترسی ندارید.")
            return
        return await func(update, context)
    return wrapper

def admin_only_cb(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        uid = update.effective_user.id if update.effective_user else None
        if uid not in Config.ADMIN_IDS:
            await update.callback_query.answer("⛔ دسترسی ندارید.", show_alert=True)
            return
        return await func(update, context)
    return wrapper


# ── Handlers ──────────────────────────────────────────────────────────────────
@admin_only
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎬 *یوتیوب → روبیکا بات*\n\n"
        "لینک یوتیوب رو بفرست، دانلود می‌کنم و\n"
        "تو *سیو مسیج روبیکات* آپلود می‌کنم 🚀\n\n"
        "📌 دستورات:\n"
        "/start — نمایش این پیام\n"
        "/status — وضعیت اتصال روبیکا",
        parse_mode="Markdown",
    )

@admin_only
async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    is_connected = rubika._client is not None and rubika._me is not None
    state = "✅ متصل" if is_connected else "❌ قطع"
    await update.message.reply_text(
        f"📡 *وضعیت روبیکا:* {state}\n"
        f"🤖 *ادمین:* `{update.effective_user.id}`",
        parse_mode="Markdown",
    )

@admin_only
async def handle_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    if not YT_PATTERN.search(url):
        await update.message.reply_text("❌ لینک یوتیوب معتبر نیست!\n\nمثال:\nhttps://youtu.be/xxxx\nhttps://youtube.com/watch?v=xxxx")
        return

    keyboard = [
        [
            InlineKeyboardButton("🎬 1080p", callback_data=f"dl|1080|{url}"),
            InlineKeyboardButton("📺 720p",  callback_data=f"dl|720|{url}"),
        ],
        [
            InlineKeyboardButton("📱 480p",  callback_data=f"dl|480|{url}"),
            InlineKeyboardButton("🎵 MP3",   callback_data=f"dl|audio|{url}"),
        ],
    ]
    await update.message.reply_text(
        "🎯 *کیفیت رو انتخاب کن:*",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown",
    )

@admin_only_cb
async def handle_quality(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    parts = query.data.split("|", 2)
    if len(parts) != 3:
        return
    _, quality, url = parts
    file_path = None

    msg = await query.edit_message_text("⏳ دریافت اطلاعات ویدیو...")

    try:
        info = await downloader.get_info(url)
        title = info.get("title", "ویدیو")
        dur = _fmt_dur(info.get("duration", 0))

        await msg.edit_text(
            f"📥 در حال دانلود...\n\n"
            f"🎬 {title}\n"
            f"⏱ {dur} | 📊 {quality if quality != 'audio' else 'MP3'}"
        )

        file_path = await downloader.download(url, quality)
        size_mb = os.path.getsize(file_path) / (1024 * 1024)

        await msg.edit_text(
            f"☁️ در حال آپلود به روبیکا...\n\n"
            f"🎬 {title}\n💾 {size_mb:.1f} MB"
        )

        await rubika.upload_to_saved(file_path, f"📹 {title}\n🔗 {url}")

        await msg.edit_text(
            f"✅ آپلود شد!\n\n"
            f"🎬 {title}\n"
            f"💾 {size_mb:.1f} MB\n\n"
            f"📌 تو سیو مسیج روبیکات آماده‌ست 🎉"
        )
        logger.info(f"✅ {title} | {size_mb:.1f} MB")

    except Exception as e:
        logger.error(f"خطا: {e}", exc_info=True)
        await msg.edit_text(f"❌ خطا:\n{e}\n\nدوباره امتحان کن.")

    finally:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"🗑 فایل موقت حذف شد: {file_path}")


# ── Helpers ───────────────────────────────────────────────────────────────────
def _fmt_dur(sec: int) -> str:
    if not sec:
        return "نامشخص"
    h, r = divmod(int(sec), 3600)
    m, s = divmod(r, 60)
    return f"{h:02d}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"


# ── Main ──────────────────────────────────────────────────────────────────────
async def post_init(app: Application):
    await rubika.connect()
    logger.info("✅ روبیکا متصل شد")

async def post_shutdown(app: Application):
    await rubika.disconnect()
    logger.info("👋 روبیکا قطع شد")

def main():
    Config.validate()
    Path(Config.DOWNLOAD_PATH).mkdir(parents=True, exist_ok=True)

    app = (
        Application.builder()
        .token(Config.TELEGRAM_BOT_TOKEN)
        .post_init(post_init)
        .post_shutdown(post_shutdown)
        .build()
    )
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_url))
    app.add_handler(CallbackQueryHandler(handle_quality, pattern=r"^dl\|"))

    logger.info("🤖 بات استارت شد — منتظر لینک...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
