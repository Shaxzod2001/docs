"""Bot rejimida muhokama guruhidagi izohlarni jonli kuzatuvchi.

Bot getUpdates orqali muhokama guruhidagi xabarlarni o'qiydi va bazaga yozadi.
Ishlashi uchun bot muhokama guruhiga admin qilib qo'shilishi va @BotFather da
privacy rejimi o'chirilgan bo'lishi kerak (/setprivacy -> Disable).
"""
import asyncio
import logging
import requests

from config import TELEGRAM_BOT_TOKEN
import database as db
import tg_bot

logger = logging.getLogger(__name__)
API = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"
_running = False


def _get_updates(offset):
    r = requests.get(
        f"{API}/getUpdates",
        params={"offset": offset, "timeout": 25, "allowed_updates": '["message"]'},
        timeout=40)
    data = r.json()
    return data.get("result", [])


async def poll_loop():
    global _running
    _running = True

    linked = None
    try:
        info = await tg_bot.get_channel_info()
        linked = info.get("linked_chat_id")
        if linked:
            logger.info(f"Izoh kuzatuvi yoqildi (guruh id: {linked})")
        else:
            logger.info("Muhokama guruhi topilmadi — izoh kuzatuvi cheklangan.")
    except Exception as e:
        logger.warning(f"Kanal ma'lumotini olishda xato: {e}")

    saved = await db.get_setting("last_update_id")
    offset = (int(saved) + 1) if saved else 0

    while _running:
        try:
            updates = await asyncio.to_thread(_get_updates, offset)
            for u in updates:
                offset = u["update_id"] + 1
                msg = u.get("message") or {}
                chat = msg.get("chat", {})
                text = msg.get("text")
                frm = msg.get("from", {})

                if not text or not frm:
                    continue
                if chat.get("type") not in ("group", "supergroup"):
                    continue
                if linked and chat.get("id") != linked:
                    continue

                await db.add_comment(
                    frm["id"], frm.get("username", ""),
                    frm.get("first_name", ""), text)
                await db.upsert_subscriber(
                    frm["id"], frm.get("username", ""),
                    frm.get("first_name", ""), bool(frm.get("is_bot")))

            if updates:
                await db.set_setting("last_update_id", offset - 1)
        except Exception as e:
            logger.warning(f"Izoh kuzatuvida xato: {e}")
            await asyncio.sleep(5)

    logger.info("Izoh kuzatuvi to'xtadi.")


def stop():
    global _running
    _running = False
