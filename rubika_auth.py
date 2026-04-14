#!/usr/bin/env python3
"""
ورود به روبیکا — فقط یک‌بار اجرا کن تا سشن ذخیره بشه
"""

import asyncio
import rubpy
from config import Config

async def main():
    print("=" * 50)
    print("  ورود به روبیکا — فقط یک بار لازمه!")
    print("=" * 50)
    print(f"  شماره: {Config.RUBIKA_PHONE}")
    print("=" * 50)
    print()
    print("  ⏳ منتظر کد تأیید روبیکا باش...")
    print("  (کد رو در اپ روبیکا یا پیامک دریافت میکنی)")
    print()

    async with rubpy.Client(
        Config.RUBIKA_SESSION,
        phone_number=Config.RUBIKA_PHONE
    ) as client:
        me = await client.get_me()

        print(f"✅ ورود موفق!")
        print(f"   نام: {getattr(me, 'first_name', 'نامشخص')}")

        # نمایش guid
        guid = getattr(me, "user_guid", None) or getattr(me, "guid", "نامشخص")
        print(f"   GUID: {guid}")
        print()
        print(f"✅ سشن ذخیره شد: {Config.RUBIKA_SESSION}.session")
        print()
        print("─" * 50)
        print("➡️  حالا بات رو اجرا کن:")
        print()
        print("   source venv/bin/activate")
        print("   python3 bot.py")
        print()
        print("   یا برای اجرا در پس‌زمینه:")
        print("   screen -S bot")
        print("   python3 bot.py")
        print("   (Ctrl+A سپس D برای minimize کردن screen)")

if __name__ == "__main__":
    asyncio.run(main())
