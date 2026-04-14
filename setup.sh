#!/bin/bash
# ═══════════════════════════════════════════════════════
#  نصب خودکار بات یوتیوب → روبیکا
#  فقط یه بار اجرا کن — همه‌چیز خودکاره
# ═══════════════════════════════════════════════════════
set -e

echo ""
echo "╔══════════════════════════════════════╗"
echo "║    نصب بات یوتیوب ← روبیکا         ║"
echo "╚══════════════════════════════════════╝"
echo ""

# ── ۱. پیش‌نیازها ─────────────────────────────────────
echo "[ 1 / 5 ]  نصب پیش‌نیازها..."
apt-get update -qq
apt-get install -y python3 python3-pip python3-venv ffmpeg git > /dev/null 2>&1
echo "  ✅ python3 + ffmpeg + git نصب شد"

# ── ۲. کلون پروژه ─────────────────────────────────────
echo "[ 2 / 5 ]  دانلود پروژه از GitHub..."
cd /root
if [ -d "yt-rubika-bot" ]; then
    echo "  ⚠️  پوشه قبلاً وجود داشت — آپدیت می‌کنم"
    cd yt-rubika-bot && git pull
else
    git clone https://github.com/Hamedi41148/yt-rubika-bot.git
    cd yt-rubika-bot
fi
echo "  ✅ پروژه آماده شد"

# ── ۳. محیط مجازی و پکیج‌ها ──────────────────────────
echo "[ 3 / 5 ]  نصب پکیج‌های Python..."
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip -q
pip install -r requirements.txt -q
echo "  ✅ پکیج‌ها نصب شد"

# ── ۴. ساخت پوشه دانلود ──────────────────────────────
echo "[ 4 / 5 ]  ساخت پوشه‌ها..."
mkdir -p downloads
echo "  ✅ پوشه downloads آماده شد"

# ── ۵. ورود روبیکا ────────────────────────────────────
echo "[ 5 / 5 ]  ورود به روبیکا..."
echo ""
echo "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  روبیکا یه کد تأیید می‌فرسته — اونو وارد کن"
echo "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
python3 rubika_auth.py

# ── پایان ─────────────────────────────────────────────
echo ""
echo "╔══════════════════════════════════════╗"
echo "║  ✅ نصب کامل شد!                    ║"
echo "╚══════════════════════════════════════╝"
echo ""
echo "  ▶️  برای اجرای بات:"
echo ""
echo "  source venv/bin/activate"
echo "  python3 bot.py"
echo ""
echo "  ▶️  برای اجرا به صورت پس‌زمینه (پیشنهادی):"
echo ""
echo "  nohup python3 bot.py > bot.log 2>&1 &"
echo "  echo \"PID: \$!\""
echo ""
