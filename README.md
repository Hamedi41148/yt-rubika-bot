# 🎬 YouTube → Rubika Bot

بات تلگرام که لینک یوتیوب می‌گیره، دانلود می‌کنه و تو **سیو مسیج روبیکا** آپلود می‌کنه.

---

## ⚡ نصب خودکار (یه دستور)

وقتی وارد سرور لینوکسیت شدی:

```bash
curl -fsSL https://raw.githubusercontent.com/Hamedi41148/yt-rubika-bot/main/setup.sh | bash
```

یا اگه ترجیح میدی دستی:

```bash
git clone https://github.com/Hamedi41148/yt-rubika-bot.git
cd yt-rubika-bot
bash setup.sh
```

---

## 🚀 اجرای بات

```bash
cd /root/yt-rubika-bot
source venv/bin/activate
python3 bot.py
```

### اجرا در پس‌زمینه (پیشنهادی — بعد از بستن VNC هم کار کنه)

```bash
cd /root/yt-rubika-bot
source venv/bin/activate
nohup python3 bot.py > bot.log 2>&1 &
echo "PID: $!"
```

برای متوقف کردن:
```bash
kill $(cat bot.pid)
# یا
pkill -f "python3 bot.py"
```

---

## 📋 مراحل نصب دستی

### ۱. پیش‌نیازها
```bash
apt-get update
apt-get install -y python3 python3-pip python3-venv ffmpeg git
```

### ۲. کلون پروژه
```bash
cd /root
git clone https://github.com/Hamedi41148/yt-rubika-bot.git
cd yt-rubika-bot
```

### ۳. محیط مجازی
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### ۴. ورود به روبیکا (فقط یه بار)
```bash
python3 rubika_auth.py
```
کد تأییدی که روبیکا می‌فرسته رو وارد کن.

### ۵. اجرای بات
```bash
python3 bot.py
```

---

## 💬 نحوه استفاده

فقط لینک یوتیوب بفرست:

```
https://youtu.be/xxxx
https://youtube.com/watch?v=xxxx
https://youtube.com/shorts/xxxx
```

بات کیفیت رو می‌پرسه (1080p / 720p / 480p / MP3) و بعد دانلود + آپلود به سیو مسیج روبیکا.

---

## ⚙️ تنظیمات (config.py)

| متغیر | مقدار |
|---|---|
| `TELEGRAM_BOT_TOKEN` | توکن بات |
| `ADMIN_IDS` | آیدی عددی ادمین |
| `RUBIKA_PHONE` | شماره روبیکا |
| `DOWNLOAD_PATH` | مسیر دانلود موقت |
