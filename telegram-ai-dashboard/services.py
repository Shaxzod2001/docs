"""Telegram va AI ni ma'lumotlar bazasi bilan bog'lovchi servis funksiyalar."""
import logging
import telegram_client as tg
import ai_engine
import database as db

logger = logging.getLogger(__name__)


async def sync_stats():
    """Kanal statistikasini yangilaydi: obunachi soni snapshot + post metrikalari."""
    info = await tg.get_channel_info()
    await db.add_stat_snapshot(info["subscriber_count"])

    posts = await tg.get_recent_posts(limit=30)
    for p in posts:
        await db.update_post_metrics(p["message_id"], p["views"], p["reactions"])

    return {
        "subscriber_count": info["subscriber_count"],
        "title": info["title"],
        "posts_updated": len(posts),
    }


async def sync_subscribers():
    """Obunachilar ro'yxatini bazaga yozadi."""
    subs = await tg.get_subscribers()
    for s in subs:
        await db.upsert_subscriber(
            s["user_id"], s["username"], s["first_name"], s["is_bot"])
    return {"synced": len(subs)}


async def analyze_interests(max_users=40):
    """Muhokama guruhidagi izohlar asosida obunachilar qiziqishlarini aniqlaydi."""
    info = await tg.get_channel_info()
    linked = info.get("linked_chat_id")
    if not linked:
        return {"error": "Kanalga bog'langan muhokama guruhi yo'q. "
                         "Izohlarsiz qiziqishlarni aniqlab bo'lmaydi."}

    texts = await tg.collect_comment_texts(linked)
    # Eng faol foydalanuvchilarni tartiblash
    ranked = sorted(texts.items(), key=lambda kv: len(kv[1]), reverse=True)
    analyzed = 0
    for user_id, msgs in ranked[:max_users]:
        if len(msgs) < 2:
            continue
        try:
            interests = ai_engine.detect_interests(msgs)
            await db.set_subscriber_interests(user_id, interests, len(msgs))
            analyzed += 1
        except Exception as e:
            logger.warning(f"Qiziqish aniqlashda xato ({user_id}): {e}")

    return {"analyzed": analyzed, "total_commenters": len(texts)}


async def send_post_now(content, source="manual"):
    """Postni darhol kanalga yuboradi va bazaga yozadi."""
    message_id = await tg.send_post(content)
    post_id = await db.add_post(content, status="sent", source=source)
    await db.mark_post_sent(post_id, message_id)
    return {"post_id": post_id, "message_id": message_id}
