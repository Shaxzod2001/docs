import asyncio
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from telegram import Bot
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHANNEL_ID, POSTS_PER_DAY
from database import get_pending_posts, mark_post_sent, save_sent_post, add_scheduled_post
from content_generator import generate_post, generate_post_from_news
from news_fetcher import get_latest_news

scheduler = AsyncIOScheduler()


async def send_pending_posts(bot: Bot):
    posts = await get_pending_posts()
    for post in posts:
        try:
            await bot.send_message(
                chat_id=TELEGRAM_CHANNEL_ID,
                text=post["content"],
                parse_mode="Markdown",
            )
            await mark_post_sent(post["id"])
            await save_sent_post(post["content"], source="scheduled")
            await asyncio.sleep(2)
        except Exception as e:
            print(f"Post yuborishda xato: {e}")


async def auto_generate_and_post(bot: Bot):
    try:
        content = generate_post()
        await bot.send_message(
            chat_id=TELEGRAM_CHANNEL_ID,
            text=content,
            parse_mode="Markdown",
        )
        await save_sent_post(content, source="auto_generated")
        print(f"[{datetime.now()}] Avtomatik post yuborildi")
    except Exception as e:
        print(f"Avtomatik post xatosi: {e}")


async def news_based_post(bot: Bot):
    try:
        news_items = await get_latest_news(limit=3)
        if not news_items:
            return

        import random
        item = random.choice(news_items)
        content = generate_post_from_news(item.title, item.summary)

        if item.url:
            content += f"\n\n🔗 [Manba]({item.url})"

        await bot.send_message(
            chat_id=TELEGRAM_CHANNEL_ID,
            text=content,
            parse_mode="Markdown",
        )
        await save_sent_post(content, source="news")
        print(f"[{datetime.now()}] Yangilik asosida post yuborildi: {item.title}")
    except Exception as e:
        print(f"Yangilik posti xatosi: {e}")


def setup_scheduler(bot: Bot):
    # Rejalashtirilgan postlarni tekshirish (har 5 daqiqada)
    scheduler.add_job(
        send_pending_posts,
        trigger="interval",
        minutes=5,
        args=[bot],
        id="check_scheduled_posts",
    )

    # Avtomatik kontent yaratish (ertalab 9:00)
    scheduler.add_job(
        auto_generate_and_post,
        trigger=CronTrigger(hour=9, minute=0),
        args=[bot],
        id="morning_post",
    )

    # Yangiliklar asosida post (tushdan keyin 14:00)
    scheduler.add_job(
        news_based_post,
        trigger=CronTrigger(hour=14, minute=0),
        args=[bot],
        id="news_post",
    )

    # Kechki ta'lim posti (18:00)
    if POSTS_PER_DAY >= 3:
        scheduler.add_job(
            auto_generate_and_post,
            trigger=CronTrigger(hour=18, minute=0),
            args=[bot],
            id="evening_post",
        )

    scheduler.start()
    print("Scheduler ishga tushdi")


def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown()
