import anthropic
from config import ANTHROPIC_API_KEY, CHANNEL_TOPIC, CHANNEL_LANGUAGE

_client = None


def get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    return _client


LANGUAGE_NAMES = {
    "uz": "o'zbek tilida",
    "ru": "rus tilida",
    "en": "ingliz tilida",
}

SYSTEM_PROMPT = """Sen ta'lim kanali uchun kontent yaratuvchi AI agentsan.
Sening vazifang:
1. Qiziqarli va foydali ta'lim postlari yozish
2. Emoji va formatlash ishlatish
3. Postlarni qisqa, aniq va tushunarli qilish
4. Telegram formatida (markdown) yozish
5. Har doim ijobiy va rag'batlantiruvchi ton ushlab turish"""


def generate_post(topic: str | None = None, custom_prompt: str | None = None) -> str:
    client = get_client()
    lang = LANGUAGE_NAMES.get(CHANNEL_LANGUAGE, "o'zbek tilida")

    if custom_prompt:
        user_message = f"{custom_prompt}\n\nJavobni {lang} yozing."
    elif topic:
        user_message = (
            f"'{topic}' mavzusida Telegram kanal posti yoz. "
            f"Post {lang} bo'lsin. "
            f"Post qiziqarli, foydali va ta'limiy bo'lsin. "
            f"Emoji ishlatish mumkin. 200-400 so'z bo'lsin."
        )
    else:
        user_message = (
            f"'{CHANNEL_TOPIC}' kanali uchun bugun yangi ta'limiy post yoz. "
            f"Post {lang} bo'lsin. "
            f"Mavzu tanlang va qiziqarli ma'lumot bering. "
            f"Emoji ishlatish mumkin. 200-400 so'z bo'lsin."
        )

    message = client.messages.create(
        model="claude-opus-4-8",
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
    )
    return message.content[0].text


def generate_post_from_news(news_title: str, news_summary: str) -> str:
    client = get_client()
    lang = LANGUAGE_NAMES.get(CHANNEL_LANGUAGE, "o'zbek tilida")

    user_message = (
        f"Quyidagi yangilik asosida Telegram kanal posti yoz:\n\n"
        f"Sarlavha: {news_title}\n"
        f"Qisqacha: {news_summary}\n\n"
        f"Post {lang} bo'lsin. "
        f"Ta'limiy va rag'batlantiruvchi tarzda yoz. "
        f"Emoji ishlatish mumkin. 150-300 so'z bo'lsin."
    )

    message = client.messages.create(
        model="claude-opus-4-8",
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
    )
    return message.content[0].text


def answer_question(question: str) -> str:
    client = get_client()
    lang = LANGUAGE_NAMES.get(CHANNEL_LANGUAGE, "o'zbek tilida")

    user_message = (
        f"Kanal a'zosi shu savolni berdi: '{question}'\n\n"
        f"Savolga {lang} javob ber. "
        f"Javob aniq, to'liq va foydali bo'lsin. "
        f"Telegram formatida yoz."
    )

    message = client.messages.create(
        model="claude-opus-4-8",
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
    )
    return message.content[0].text


def generate_weekly_plan() -> str:
    client = get_client()
    lang = LANGUAGE_NAMES.get(CHANNEL_LANGUAGE, "o'zbek tilida")

    user_message = (
        f"'{CHANNEL_TOPIC}' Telegram kanali uchun 1 haftalik kontent rejasini tuz. "
        f"Har kun uchun 2-3 ta post mavzusi taklif qil. "
        f"Reja {lang} bo'lsin. "
        f"Markdown formatida chiroyli qilib yoz."
    )

    message = client.messages.create(
        model="claude-opus-4-8",
        max_tokens=2048,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
    )
    return message.content[0].text
