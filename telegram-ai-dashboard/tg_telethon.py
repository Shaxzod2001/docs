import asyncio
from collections import defaultdict
from io import BytesIO
from telethon import TelegramClient
from telethon.tl.custom import Button
from telethon.tl.functions.channels import GetFullChannelRequest
from config import API_ID, API_HASH, SESSION_NAME, CHANNEL
import images

_client = None


async def get_client():
    """Mavjud sessiya bilan ulangan Telethon clientni qaytaradi."""
    global _client
    if _client is None:
        _client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
    if not _client.is_connected():
        await _client.connect()
    if not await _client.is_user_authorized():
        raise RuntimeError(
            "Telegram sessiya topilmadi. Avval 'python login.py' ni ishga tushiring."
        )
    return _client


async def is_authorized():
    try:
        global _client
        if _client is None:
            _client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
        if not _client.is_connected():
            await _client.connect()
        return await _client.is_user_authorized()
    except Exception:
        return False


async def send_post(text):
    return await send_rich_post(text)


async def send_rich_post(text, image_url=None, buttons=None):
    client = await get_client()
    btns = [[Button.url(b["text"], b["url"])] for b in buttons] if buttons else None

    if image_url:
        # URL to'g'ridan-to'g'ri yuborish — Telethon o'zi yuklab oladi
        try:
            msg = await client.send_file(
                CHANNEL, image_url, caption=text[:1024], parse_mode="md", buttons=btns)
            return msg.id
        except Exception:
            pass
        # Fallback: qo'lda yuklab bayt sifatida yuborish
        data = await asyncio.to_thread(images.fetch_image, image_url)
        if data:
            bio = BytesIO(data)
            bio.name = "image.jpg"
            msg = await client.send_file(
                CHANNEL, bio, caption=text[:1024], parse_mode="md", buttons=btns)
            return msg.id

    msg = await client.send_message(CHANNEL, text, parse_mode="md", buttons=btns)
    return msg.id


async def get_channel_info():
    client = await get_client()
    full = await client(GetFullChannelRequest(CHANNEL))
    return {
        "subscriber_count": full.full_chat.participants_count,
        "linked_chat_id": full.full_chat.linked_chat_id,
        "title": getattr(full.chats[0], "title", "") if full.chats else "",
    }


async def get_recent_posts(limit=30):
    client = await get_client()
    results = []
    async for msg in client.iter_messages(CHANNEL, limit=limit):
        text = msg.message or ""
        if not text:
            continue
        reactions = 0
        if msg.reactions and msg.reactions.results:
            reactions = sum(r.count for r in msg.reactions.results)
        results.append({
            "message_id": msg.id,
            "text": text[:200],
            "views": msg.views or 0,
            "reactions": reactions,
            "date": msg.date.isoformat() if msg.date else None,
        })
    return results


async def get_subscribers(limit=2000):
    """Kanal obunachilari ro'yxati (admin huquqi kerak)."""
    client = await get_client()
    subs = []
    async for user in client.iter_participants(CHANNEL, limit=limit):
        subs.append({
            "user_id": user.id,
            "username": user.username or "",
            "first_name": user.first_name or "",
            "is_bot": bool(user.bot),
        })
    return subs


async def collect_comment_texts(linked_chat_id, limit=800):
    """Bog'langan muhokama guruhidan har bir foydalanuvchi xabarlarini yig'adi."""
    texts = defaultdict(list)
    if not linked_chat_id:
        return texts
    client = await get_client()
    async for msg in client.iter_messages(linked_chat_id, limit=limit):
        if msg.sender_id and msg.message:
            texts[msg.sender_id].append(msg.message)
    return texts
