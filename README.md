# 🎬 یوتیوب → روبیکا بات

بات تلگرام که ویدیوهای یوتیوب رو دانلود میکنه و در سیو مسیج روبیکا آپلود میکنه.

## نصب روی سرور (یک بار)

```bash
wget -O setup.sh https://raw.githubusercontent.com/Hamedi41148/yt-rubika-bot/main/setup.sh
chmod +x setup.sh
bash setup.sh
```

## اجرای بات

```bash
cd /root/yt-rubika-bot
source venv/bin/activate
screen -S bot
python3 bot.py
# Ctrl+A سپس D برای مینیمایز
```

## دستورات بات

- لینک یوتیوب → انتخاب کیفیت و دانلود+آپلود خودکار
- `/start` — نمایش راهنما
- `/status` — وضعیت اتصال روبیکا
- `/reconnect` — اتصال مجدد روبیکا

## مشکل‌یابی

```bash
# دیدن لاگ زنده
tail -f /root/yt-rubika-bot/bot.log

# برگشت به screen
screen -r bot
```
