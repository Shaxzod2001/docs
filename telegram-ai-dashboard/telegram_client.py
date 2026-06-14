"""Telegram backend dispatcher: rejimga qarab bot yoki user akkauntni tanlaydi."""
from config import TELEGRAM_MODE

if TELEGRAM_MODE == "user":
    from tg_telethon import (
        is_authorized,
        send_post,
        send_rich_post,
        get_channel_info,
        get_recent_posts,
        get_subscribers,
        collect_comment_texts,
    )
else:
    from tg_bot import (
        is_authorized,
        send_post,
        send_rich_post,
        get_channel_info,
        get_recent_posts,
        get_subscribers,
        collect_comment_texts,
    )

__all__ = [
    "is_authorized",
    "send_post",
    "send_rich_post",
    "get_channel_info",
    "get_recent_posts",
    "get_subscribers",
    "collect_comment_texts",
]
