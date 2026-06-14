import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

ADMIN_USER_IDS = [
    int(uid.strip())
    for uid in os.getenv("ADMIN_USER_IDS", "").split(",")
    if uid.strip().isdigit()
]

CHANNEL_TOPIC = os.getenv("CHANNEL_TOPIC", "Ta'lim va o'rganish")
CHANNEL_LANGUAGE = os.getenv("CHANNEL_LANGUAGE", "uz")
POSTS_PER_DAY = int(os.getenv("POSTS_PER_DAY", "3"))

RSS_FEEDS = [
    feed.strip()
    for feed in os.getenv("RSS_FEEDS", "").split(",")
    if feed.strip()
]

DATABASE_PATH = os.getenv("DATABASE_PATH", "bot_data.db")
