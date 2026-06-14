import os
from dotenv import load_dotenv

load_dotenv()

# Telegram bot token (@BotFather dan) - BOT REJIMI
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

# Telegram user akkaunt (my.telegram.org dan) - TO'LIQ REJIM (ixtiyoriy)
API_ID = int(os.getenv("TELEGRAM_API_ID") or "0")
API_HASH = os.getenv("TELEGRAM_API_HASH", "")
PHONE = os.getenv("TELEGRAM_PHONE", "")
SESSION_NAME = os.getenv("SESSION_NAME", "user_session")

# Kanal (username yoki -100... ID)
CHANNEL = os.getenv("TELEGRAM_CHANNEL", "")

# Rejimni aniqlash: user akkaunt kalitlari bo'lsa "user", aks holda "bot"
if API_ID and API_HASH:
    TELEGRAM_MODE = "user"
elif TELEGRAM_BOT_TOKEN:
    TELEGRAM_MODE = "bot"
else:
    TELEGRAM_MODE = "none"

# Groq AI (console.groq.com dan)
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

# Kanal sozlamalari
CHANNEL_TOPIC = os.getenv("CHANNEL_TOPIC", "Kiberxavfsizlik va IT")
CHANNEL_LANGUAGE = os.getenv("CHANNEL_LANGUAGE", "uz")

# Avtomatik post vaqtlari (HH:MM, vergul bilan)
AUTO_POST_TIMES = [
    t.strip() for t in os.getenv("AUTO_POST_TIMES", "09:00,14:00,18:00").split(",")
    if t.strip()
]

# Ma'lumotlar bazasi
DATABASE_PATH = os.getenv("DATABASE_PATH", "dashboard.db")

# Veb server
WEB_HOST = os.getenv("WEB_HOST") or "127.0.0.1"
WEB_PORT = int(os.getenv("WEB_PORT") or "8000")

# Statistika yangilash oralig'i (daqiqa)
STATS_REFRESH_MINUTES = int(os.getenv("STATS_REFRESH_MINUTES") or "30")

# Postlarda rasm bo'lsinmi (avtomatik postlar uchun)
POST_WITH_IMAGE = (os.getenv("POST_WITH_IMAGE", "true").lower() != "false")


def _default_buttons():
    """Postlar uchun standart inline tugmalar."""
    btns = []
    if CHANNEL.startswith("@"):
        btns.append({"text": "📢 Kanalga obuna", "url": f"https://t.me/{CHANNEL[1:]}"})
    # .env orqali qo'shimcha tugma (ixtiyoriy)
    extra_text = os.getenv("POST_BUTTON_TEXT")
    extra_url = os.getenv("POST_BUTTON_URL")
    if extra_text and extra_url:
        btns.append({"text": extra_text, "url": extra_url})
    return btns


POST_BUTTONS = _default_buttons()
