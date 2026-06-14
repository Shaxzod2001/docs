"""Bot API orqali Telegram bilan ishlash (bot rejimi)."""
import asyncio
import json
import requests
from config import TELEGRAM_BOT_TOKEN, CHANNEL
import images

API = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"


def _call(method, **params):
    r = requests.post(f"{API}/{method}", json=params, timeout=40)
    data = r.json()
    if not data.get("ok"):
        raise RuntimeError(data.get("description", "Telegram API xato"))
    return data["result"]


def _send_text(text, reply_markup):
    params = {"chat_id": CHANNEL, "text": text}
    if reply_markup:
        params["reply_markup"] = reply_markup
    try:
        return _call("sendMessage", parse_mode="Markdown", **params)["message_id"]
    except Exception:
        # Markdown buzilgan bo'lsa, oddiy matn bilan qayta yuborish
        return _call("sendMessage", **params)["message_id"]


def _send_photo_bytes(caption, data, reply_markup):
    def _post(use_md):
        form = {"chat_id": CHANNEL, "caption": caption[:1024]}
        if use_md:
            form["parse_mode"] = "Markdown"
        if reply_markup:
            form["reply_markup"] = json.dumps(reply_markup)
        files = {"photo": ("image.jpg", data)}
        r = requests.post(f"{API}/sendPhoto", data=form, files=files, timeout=120)
        return r.json()

    res = _post(True)
    if not res.get("ok"):
        res = _post(False)
    if not res.get("ok"):
        raise RuntimeError(res.get("description", "sendPhoto xato"))
    return res["result"]["message_id"]


async def is_authorized():
    try:
        await asyncio.to_thread(_call, "getMe")
        return True
    except Exception:
        return False


async def send_post(text):
    return await send_rich_post(text)


async def send_rich_post(text, image_url=None, buttons=None):
    """Rasm va inline tugmalar bilan post yuboradi."""
    reply_markup = None
    if buttons:
        reply_markup = {"inline_keyboard": [[b] for b in buttons]}

    if image_url:
        data = await asyncio.to_thread(images.fetch_image, image_url)
        if data:
            return await asyncio.to_thread(
                _send_photo_bytes, text, data, reply_markup)

    return await asyncio.to_thread(_send_text, text, reply_markup)


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
