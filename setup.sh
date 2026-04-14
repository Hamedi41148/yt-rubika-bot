#!/bin/bash
# ════════════════════════════════════════════════════════
#  نصب خودکار بات یوتیوب → روبیکا
#  فقط یه بار اجرا کن — همه‌چیز خودکاره
#  مناسب Ubuntu/Debian — سرور aeza.net
# ════════════════════════════════════════════════════════
set -e

echo ""
echo "╔══════════════════════════════════════╗"
echo "║    نصب بات یوتیوب ← روبیکا          ║"
echo "╚══════════════════════════════════════╝"
echo ""

# ── ۱. پیش‌نیازها ─────────────────────────────────────
echo "[ 1 / 6 ]  نصب پیش‌نیازها..."
apt-get update -qq
apt-get install -y python3 python3-pip python3-venv ffmpeg git screen > /dev/null 2>&1
echo "  ✅ python3 + ffmpeg + git + screen نصب شد"

# ── ۲. کلون پروژه از GitHub ───────────────────────────
echo "[ 2 / 6 ]  دانلود پروژه از GitHub..."
cd /root
if [ -d "yt-rubika-bot" ]; then
    echo "  ⚠️  پوشه قبلاً وجود داشت — آپدیت میکنم"
    cd yt-rubika-bot && git pull
else
    git clone https://github.com/Hamedi41148/yt-rubika-bot.git
    cd yt-rubika-bot
fi
echo "  ✅ پروژه دانلود شد"

# ── ۳. محیط مجازی Python ─────────────────────────────
echo "[ 3 / 6 ]  ساخت محیط مجازی Python..."
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip -q
echo "  ✅ محیط مجازی آماده شد"

# ── ۴. نصب پکیج‌ها ────────────────────────────────────
echo "[ 4 / 6 ]  نصب پکیج‌های Python..."
pip install -r requirements.txt -q
# آپدیت yt-dlp به آخرین نسخه
pip install --upgrade yt-dlp -q
echo "  ✅ پکیج‌ها نصب شد + yt-dlp آپدیت شد"

# ── ۵. ساخت پوشه‌ها ───────────────────────────────────
echo "[ 5 / 6 ]  ساخت پوشه‌ها..."
mkdir -p downloads
echo "  ✅ پوشه downloads آماده شد"

# ── ۶. ورود به روبیکا ────────────────────────────────
echo "[ 6 / 6 ]  ورود به روبیکا..."
echo ""
echo "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  روبیکا یه کد تأیید میفرسته — اونو وارد کن"
echo "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
python3 rubika_auth.py

# ── پایان ─────────────────────────────────────────────
echo ""
echo "╔══════════════════════════════════════════╗"
echo "║  ✅ نصب کامل شد!                         ║"
echo "╚══════════════════════════════════════════╝"
echo ""
echo "  ▶️  اجرای بات (روش پیشنهادی با screen):"
echo ""
echo "  cd /root/yt-rubika-bot"
echo "  source venv/bin/activate"
echo "  screen -S bot"
echo "  python3 bot.py"
echo ""
echo "  بعد از اجرا، برای minimize کردن پنجره:"
echo "  Ctrl+A سپس D"
echo ""
echo "  برای برگشت به screen:"
echo "  screen -r bot"
echo ""
echo "  برای دیدن لاگ‌ها:"
echo "  tail -f /root/yt-rubika-bot/bot.log"
echo ""
