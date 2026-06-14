"""Bot API orqali Telegram bilan ishlash (bot rejimi)."""
import asyncio
import requests
from config import TELEGRAM_BOT_TOKEN, CHANNEL

API = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"


def _call(method, **params):
    r = requests.post(f"{API}/{method}", json=params, timeout=40)
    data = r.json()
    if not data.get("ok"):
        raise RuntimeError(data.get("description", "Telegram API xato"))
    return data["result"]


async def is_authorized():
    try:
        await asyncio.to_thread(_call, "getMe")
        return True
    except Exception:
        return False


async def send_post(text):
    res = await asyncio.to_thread(
        _call, "sendMessage", chat_id=CHANNEL, text=text, parse_mode="Markdown")
    return res["message_id"]


async def get_channel_info():
    chat = await asyncio.to_thread(_call, "getChat", chat_id=CHANNEL)
    count = await asyncio.to_thread(_call, "getChatMemberCount", chat_id=CHANNEL)
    return {
        "subscriber_count": count,
        "linked_chat_id": chat.get("linked_chat_id"),
        "title": chat.get("title", ""),
    }


async def get_recent_posts(limit=30):
    # Bot API post ko'rishlari/reaksiyalarini tarixiy bermaydi
    return []


async def get_subscribers(limit=2000):
    raise RuntimeError(
        "Bot rejimida to'liq obunachilar ro'yxatini olib bo'lmaydi. "
        "Faqat izoh yozgan obunachilar kuzatiladi.")


async def collect_comment_texts(linked_chat_id, limit=800):
    raise RuntimeError("Bot rejimida izohlar jonli kuzatuv orqali yig'iladi.")
