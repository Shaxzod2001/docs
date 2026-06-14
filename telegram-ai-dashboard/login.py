#!/usr/bin/env python3
"""
Telegram sessiyasini birinchi marta yaratish uchun skript.
Bir marta ishga tushiring: python login.py
Telefon raqamingizga kelgan kodni kiriting. Sessiya fayli saqlanadi.
"""
import asyncio
from telethon import TelegramClient
from config import API_ID, API_HASH, PHONE, SESSION_NAME


async def main():
    if not API_ID or not API_HASH:
        print("XATO: TELEGRAM_API_ID va TELEGRAM_API_HASH .env faylda yo'q.")
        print("Ularni my.telegram.org saytidan oling.")
        return

    client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
    await client.start(phone=PHONE or None)

    me = await client.get_me()
    print(f"\n✅ Muvaffaqiyatli kirdingiz: {me.first_name} (@{me.username})")
    print(f"Sessiya fayli saqlandi: {SESSION_NAME}.session")
    print("Endi 'python app.py' ni ishga tushiring.")

    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
