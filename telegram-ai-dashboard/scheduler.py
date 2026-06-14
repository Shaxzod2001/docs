import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

import database as db
import ai_engine
import services
from config import AUTO_POST_TIMES, STATS_REFRESH_MINUTES

logger = logging.getLogger(__name__)
scheduler = AsyncIOScheduler()


async def _send_due_posts():
    """Vaqti kelgan rejalashtirilgan postlarni yuboradi."""
    due = await db.get_due_posts()
    for post in due:
        try:
            import telegram_client as tg
            message_id = await tg.send_post(post["content"])
            await db.mark_post_sent(post["id"], message_id)
            logger.info(f"Rejalashtirilgan post yuborildi: #{post['id']}")
        except Exception as e:
            logger.error(f"Post yuborishda xato (#{post['id']}): {e}")


async def _auto_generate_and_post():
    """AI bilan avtomatik post yaratib kanalga joylaydi."""
    try:
        content = ai_engine.generate_post()
        await services.send_post_now(content, source="auto")
        logger.info("Avtomatik post yaratildi va yuborildi.")
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
