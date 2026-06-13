#!/usr/bin/env python3
"""
Telegram kanal AI agenti - Ta'lim kanallari uchun
"""

import asyncio
import logging
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)
from config import (
    TELEGRAM_BOT_TOKEN,
    TELEGRAM_CHANNEL_ID,
    ADMIN_USER_IDS,
    CHANNEL_TOPIC,
    OLLAMA_API_KEY,
)
from database import (
    init_db,
    add_scheduled_post,
    get_scheduled_posts,
    delete_scheduled_post,
    save_sent_post,
    get_setting,
    set_setting,
)
from content_generator import (
    generate_post,
    generate_post_from_news,
    answer_question,
    generate_weekly_plan,
)
from news_fetcher import get_latest_news
from scheduler import setup_scheduler, stop_scheduler

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_USER_IDS


def admin_only(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_user or not is_admin(update.effective_user.id):
            await update.message.reply_text("⛔ Bu buyruq faqat adminlar uchun.")
            return
        return await func(update, context)
    wrapper.__name__ = func.__name__
    return wrapper


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if is_admin(user.id):
        text = (
            f"👋 Salom, {user.first_name}!\n\n"
            f"🤖 **Telegram Kanal AI Agenti** ishga tayyor!\n\n"
            f"📚 Kanal mavzusi: *{CHANNEL_TOPIC}*\n\n"
            f"**Admin buyruqlari:**\n"
            f"/post — Yangi post yaratish\n"
            f"/news — Yangiliklar asosida post\n"
            f"/schedule — Post rejalashtirish\n"
            f"/list — Rejalashtirilgan postlar\n"
            f"/plan — Haftalik reja\n"
            f"/stats — Statistika\n"
            f"/topic — Mavzu o'zgartirish\n\n"
            f"💡 Oddiy xabar yuboring — AI javob beradi!"
        )
    else:
        text = (
            f"👋 Salom, {user.first_name}!\n\n"
            f"🤖 Men *{CHANNEL_TOPIC}* kanalining AI yordamchisiman.\n\n"
            f"Savol bering — javob beraman! 📚"
        )
    await update.message.reply_text(text, parse_mode="Markdown")


@admin_only
async def create_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    topic = " ".join(context.args) if context.args else None

    await update.message.reply_text("⏳ Post yaratilmoqda...")

    try:
        content = generate_post(topic=topic)

        keyboard = [
            [
                InlineKeyboardButton("✅ Kanalga yuborish", callback_data=f"send_post"),
                InlineKeyboardButton("🔄 Qayta yaratish", callback_data=f"regenerate_post"),
            ],
            [
                InlineKeyboardButton("📅 Rejalashtirish", callback_data="schedule_post"),
                InlineKeyboardButton("❌ Bekor qilish", callback_data="cancel"),
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        context.user_data["pending_post"] = content
        context.user_data["pending_topic"] = topic

        await update.message.reply_text(
            f"📝 **Yaratilgan post:**\n\n{content}",
            parse_mode="Markdown",
            reply_markup=reply_markup,
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Xato: {e}")


@admin_only
async def news_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📰 Yangiliklar yuklanmoqda...")

    try:
        news_items = await get_latest_news(limit=5)
        if not news_items:
            await update.message.reply_text("❌ Yangiliklar topilmadi.")
            return

        text = "📰 **Yangiliklar:**\n\n"
        for i, item in enumerate(news_items, 1):
            text += f"{i}. [{item.title}]({item.url})\n   _{item.source}_\n\n"

        keyboard = [
            [InlineKeyboardButton(f"📝 {i+1}-yangilik", callback_data=f"news_{i}")]
            for i in range(len(news_items))
        ]
        keyboard.append([InlineKeyboardButton("❌ Bekor qilish", callback_data="cancel")])

        context.user_data["news_items"] = [
            {"title": n.title, "summary": n.summary, "url": n.url}
            for n in news_items
        ]

        await update.message.reply_text(
            text,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Xato: {e}")


@admin_only
async def schedule_post_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📅 **Post rejalashtirish:**\n\n"
        "Quyidagi formatda yuboring:\n"
        "`/schedule YYYY-MM-DD HH:MM post matni`\n\n"
        "Misol:\n"
        "`/schedule 2024-12-25 09:00 Yangi yil bilan!`",
        parse_mode="Markdown",
    )

    if len(context.args) >= 3:
        try:
            date_str = context.args[0]
            time_str = context.args[1]
            content = " ".join(context.args[2:])

            scheduled_time = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")

            if scheduled_time <= datetime.now():
                await update.message.reply_text("❌ Vaqt o'tib ketgan. Kelajak vaqtni kiriting.")
                return

            post_id = await add_scheduled_post(content, scheduled_time)
            await update.message.reply_text(
                f"✅ Post rejalashtirildi!\n"
                f"🆔 ID: {post_id}\n"
                f"📅 Vaqt: {scheduled_time.strftime('%Y-%m-%d %H:%M')}",
            )
        except ValueError:
            await update.message.reply_text("❌ Noto'g'ri format. YYYY-MM-DD HH:MM ko'rinishida kiriting.")


@admin_only
async def list_scheduled(update: Update, context: ContextTypes.DEFAULT_TYPE):
    posts = await get_scheduled_posts()

    if not posts:
        await update.message.reply_text("📭 Rejalashtirilgan postlar yo'q.")
        return

    text = "📅 **Rejalashtirilgan postlar:**\n\n"
    for post in posts:
        scheduled = post["scheduled_time"][:16]
        preview = post["content"][:80] + "..." if len(post["content"]) > 80 else post["content"]
        text += f"🆔 `{post['id']}` | 🕐 {scheduled}\n{preview}\n\n"

    keyboard = [
        [InlineKeyboardButton(f"🗑 #{p['id']} o'chirish", callback_data=f"delete_post_{p['id']}")]
        for p in posts
    ]

    await update.message.reply_text(
        text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


@admin_only
async def weekly_plan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⏳ Haftalik reja tayyorlanmoqda...")
    try:
        plan = generate_weekly_plan()
        await update.message.reply_text(f"📅 **Haftalik kontent rejasi:**\n\n{plan}", parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ Xato: {e}")


@admin_only
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    scheduled = await get_scheduled_posts()
    total_scheduled = len(scheduled)

    text = (
        f"📊 **Statistika:**\n\n"
        f"📅 Rejalashtirilgan postlar: {total_scheduled}\n"
        f"📚 Kanal mavzusi: {CHANNEL_TOPIC}\n"
        f"🤖 Status: Ishlamoqda ✅"
    )
    await update.message.reply_text(text, parse_mode="Markdown")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    text = update.message.text
    user = update.effective_user

    if is_admin(user.id):
        # Admin schedule input
        if context.user_data.get("awaiting_schedule_time"):
            content = context.user_data.pop("pending_post_for_schedule", "")
            try:
                scheduled_time = datetime.strptime(text.strip(), "%Y-%m-%d %H:%M")
                post_id = await add_scheduled_post(content, scheduled_time)
                context.user_data.pop("awaiting_schedule_time", None)
                await update.message.reply_text(
                    f"✅ Post rejalashtirildi! ID: {post_id}\n"
                    f"Vaqt: {scheduled_time.strftime('%Y-%m-%d %H:%M')}"
                )
            except ValueError:
                await update.message.reply_text("❌ Format: YYYY-MM-DD HH:MM")
            return

    # Savollarga AI bilan javob berish
    await update.message.reply_text("💭 O'ylanmoqdaman...")
    try:
        answer = answer_question(text)
        await update.message.reply_text(answer, parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ Xato yuz berdi: {e}")


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "cancel":
        await query.edit_message_text("❌ Bekor qilindi.")

    elif data == "send_post":
        content = context.user_data.get("pending_post")
        if not content:
            await query.edit_message_text("❌ Post topilmadi.")
            return
        try:
            bot = context.bot
            await bot.send_message(
                chat_id=TELEGRAM_CHANNEL_ID,
                text=content,
                parse_mode="Markdown",
            )
            await save_sent_post(content, source="manual")
            await query.edit_message_text("✅ Post kanalga yuborildi!")
        except Exception as e:
            await query.edit_message_text(f"❌ Xato: {e}")

    elif data == "regenerate_post":
        topic = context.user_data.get("pending_topic")
        await query.edit_message_text("⏳ Qayta yaratilmoqda...")
        try:
            content = generate_post(topic=topic)
            context.user_data["pending_post"] = content

            keyboard = [
                [
                    InlineKeyboardButton("✅ Kanalga yuborish", callback_data="send_post"),
                    InlineKeyboardButton("🔄 Qayta yaratish", callback_data="regenerate_post"),
                ],
                [
                    InlineKeyboardButton("📅 Rejalashtirish", callback_data="schedule_post"),
                    InlineKeyboardButton("❌ Bekor qilish", callback_data="cancel"),
                ],
            ]
            await query.edit_message_text(
                f"📝 **Yangi post:**\n\n{content}",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(keyboard),
            )
        except Exception as e:
            await query.edit_message_text(f"❌ Xato: {e}")

    elif data == "schedule_post":
        content = context.user_data.get("pending_post")
        context.user_data["pending_post_for_schedule"] = content
        context.user_data["awaiting_schedule_time"] = True
        await query.edit_message_text(
            "📅 Qachon yuborish kerak?\nFormat: `YYYY-MM-DD HH:MM`\nMisol: `2024-12-25 09:00`",
            parse_mode="Markdown",
        )

    elif data.startswith("news_"):
        idx = int(data.split("_")[1])
        news_items = context.user_data.get("news_items", [])
        if idx >= len(news_items):
            await query.edit_message_text("❌ Yangilik topilmadi.")
            return

        item = news_items[idx]
        await query.edit_message_text("⏳ Post yaratilmoqda...")
        try:
            content = generate_post_from_news(item["title"], item["summary"])
            if item.get("url"):
                content += f"\n\n🔗 [Manba]({item['url']})"
            context.user_data["pending_post"] = content

            keyboard = [
                [
                    InlineKeyboardButton("✅ Kanalga yuborish", callback_data="send_post"),
                    InlineKeyboardButton("📅 Rejalashtirish", callback_data="schedule_post"),
                ],
                [InlineKeyboardButton("❌ Bekor qilish", callback_data="cancel")],
            ]
            await query.edit_message_text(
                f"📝 **Yangilik asosida post:**\n\n{content}",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(keyboard),
            )
        except Exception as e:
            await query.edit_message_text(f"❌ Xato: {e}")

    elif data.startswith("delete_post_"):
        post_id = int(data.split("_")[-1])
        deleted = await delete_scheduled_post(post_id)
        if deleted:
            await query.edit_message_text(f"✅ Post #{post_id} o'chirildi.")
        else:
            await query.edit_message_text(f"❌ Post #{post_id} topilmadi.")


async def post_init(application: Application):
    await init_db()
    setup_scheduler(application.bot)
    logger.info("Bot ishga tushdi!")


async def post_shutdown(application: Application):
    stop_scheduler()
    logger.info("Bot to'xtatildi.")


def main():
    if not TELEGRAM_BOT_TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN o'rnatilmagan!")
    if not OLLAMA_API_KEY:
        raise ValueError("OLLAMA_API_KEY o'rnatilmagan!")

    app = (
        Application.builder()
        .token(TELEGRAM_BOT_TOKEN)
        .post_init(post_init)
        .post_shutdown(post_shutdown)
        .build()
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("post", create_post))
    app.add_handler(CommandHandler("news", news_post))
    app.add_handler(CommandHandler("schedule", schedule_post_cmd))
    app.add_handler(CommandHandler("list", list_scheduled))
    app.add_handler(CommandHandler("plan", weekly_plan))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Bot polling boshlandi...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
