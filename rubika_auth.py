#!/usr/bin/env python3
"""
ورود به روبیکا — فقط یک‌بار اجرا کن تا سشن ذخیره بشه
"""

import asyncio
import rubpy

PHONE   = "+989046056562"
SESSION = "rubika_session"

async def main():
    print("=" * 45)
    print("  ورود به روبیکا")
    print("=" * 45)
    print(f"  شماره: {PHONE}")
    print("=" * 45)
    print()
    print("  ⏳ منتظر کد تأیید روبیکا باش...")
    print()

    async with rubpy.Client(SESSION, phone_number=PHONE) as client:
        me = await client.get_me()
        print(f"✅ ورود موفق!")
        print(f"   نام: {me.first_name}")
        print(f"   شناسه: {me.user_id}")
        print()
        print(f"✅ سشن ذخیره شد: {SESSION}.session")
        print()
        print("➡️  حالا بات رو استارت کن:")
        print("   python bot.py")

if __name__ == "__main__":
    asyncio.run(main())
