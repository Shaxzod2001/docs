import os
from dotenv import load_dotenv

load_dotenv()

# Telegram user akkaunt (my.telegram.org dan)
API_ID = int(os.getenv("TELEGRAM_API_ID", "0"))
API_HASH = os.getenv("TELEGRAM_API_HASH", "")
PHONE = os.getenv("TELEGRAM_PHONE", "")
SESSION_NAME = os.getenv("SESSION_NAME", "user_session")

# Kanal (username yoki -100... ID)
CHANNEL = os.getenv("TELEGRAM_CHANNEL", "")

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
WEB_HOST = os.getenv("WEB_HOST", "127.0.0.1")
WEB_PORT = int(os.getenv("WEB_PORT", "8000"))

# Statistika yangilash oralig'i (daqiqa)
STATS_REFRESH_MINUTES = int(os.getenv("STATS_REFRESH_MINUTES", "30"))
