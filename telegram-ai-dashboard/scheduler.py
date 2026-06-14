import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

import database as db
import ai_engine
import services
import images
import telegram_client as tg
from config import AUTO_POST_TIMES, STATS_REFRESH_MINUTES, POST_WITH_IMAGE, POST_BUTTONS

logger = logging.getLogger(__name__)
scheduler = AsyncIOScheduler()


async def _send_due_posts():
    """Vaqti kelgan rejalashtirilgan postlarni (rasm + tugma bilan) yuboradi."""
    due = await db.get_due_posts()
    for post in due:
        try:
            message_id = await tg.send_rich_post(
                post["content"],
                image_url=post.get("image_url"),
                buttons=POST_BUTTONS or None)
            await db.mark_post_sent(post["id"], message_id)
            logger.info(f"Rejalashtirilgan post yuborildi: #{post['id']}")
        except Exception as e:
            logger.error(f"Post yuborishda xato (#{post['id']}): {e}")


async def _auto_generate_and_post():
    """AI bilan avtomatik rasm+tugmali post yaratib kanalga joylaydi."""
    try:
        rich = ai_engine.generate_rich_post(with_image=POST_WITH_IMAGE)
        image_url = None
        if POST_WITH_IMAGE and rich.get("image_prompt"):
            image_url = images.build_image_url(rich["image_prompt"])
        await services.send_post_now(
            rich["content"], image_url=image_url, source="auto")
        logger.info("Avtomatik post (rasm+tugma) yaratildi va yuborildi.")
    except Exception as e:
        logger.error(f"Avtomatik post xatosi: {e}")


async def _refresh_stats():
    try:
        await services.sync_stats()
        logger.info("Statistika yangilandi.")
    except Exception as e:
        logger.warning(f"Statistika yangilashda xato: {e}")


def setup_scheduler():
    # Har daqiqada vaqti kelgan postlarni tekshirish
    scheduler.add_job(_send_due_posts, IntervalTrigger(minutes=1),
                      id="send_due_posts", replace_existing=True)

    # Statistikani davriy yangilash
    scheduler.add_job(_refresh_stats,
                      IntervalTrigger(minutes=STATS_REFRESH_MINUTES),
                      id="refresh_stats", replace_existing=True)

    # Belgilangan vaqtlarda avtomatik post
    for i, t in enumerate(AUTO_POST_TIMES):
        try:
            hour, minute = map(int, t.split(":"))
            scheduler.add_job(
                _auto_generate_and_post,
                CronTrigger(hour=hour, minute=minute),
                id=f"auto_post_{i}", replace_existing=True)
        except ValueError:
            logger.warning(f"Noto'g'ri vaqt formati: {t}")

    scheduler.start()
    logger.info("Scheduler ishga tushdi.")


def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown(wait=False)
