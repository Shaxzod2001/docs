import requests
from config import OLLAMA_API_KEY, CHANNEL_TOPIC, CHANNEL_LANGUAGE

SYSTEM_PROMPT = (
    "Sen ta'lim kanali uchun kontent yaratuvchi AI agentsan. "
    "Qiziqarli va foydali postlar yoz. "
    "Telegram markdown formatidan foydalan. "
    "Har doim ijobiy va rag'batlantiruvchi ton ushlab tur."
)

LANGUAGE_NAMES = {
    "uz": "o'zbek tilida",
    "ru": "rus tilida",
    "en": "ingliz tilida",
}


def _ask(prompt: str) -> str:
    response = requests.post(
        "https://api.ollama.com/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OLLAMA_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": "llama3.2",
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            "max_tokens": 1024,
        },
        timeout=30,
    )
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]


def generate_post(topic: str | None = None, custom_prompt: str | None = None) -> str:
    lang = LANGUAGE_NAMES.get(CHANNEL_LANGUAGE, "o'zbek tilida")

    if custom_prompt:
        return _ask(f"{custom_prompt}\n\nJavobni {lang} yozing.")

    if topic:
        return _ask(
            f"'{topic}' mavzusida Telegram kanal posti yoz. "
            f"Post {lang} bo'lsin. Qiziqarli, foydali va ta'limiy bo'lsin. "
            f"Emoji ishlatish mumkin. 200-400 so'z."
        )

    return _ask(
        f"'{CHANNEL_TOPIC}' kanali uchun yangi ta'limiy post yoz. "
        f"Post {lang} bo'lsin. Mavzu tanlang, qiziqarli ma'lumot bering. "
        f"Emoji mumkin. 200-400 so'z."
    )


def generate_post_from_news(news_title: str, news_summary: str) -> str:
    lang = LANGUAGE_NAMES.get(CHANNEL_LANGUAGE, "o'zbek tilida")
    return _ask(
        f"Quyidagi yangilik asosida Telegram kanal posti yoz:\n\n"
        f"Sarlavha: {news_title}\n"
        f"Qisqacha: {news_summary}\n\n"
        f"Post {lang} bo'lsin. Ta'limiy va rag'batlantiruvchi. "
        f"Emoji mumkin. 150-300 so'z."
    )


def answer_question(question: str) -> str:
    lang = LANGUAGE_NAMES.get(CHANNEL_LANGUAGE, "o'zbek tilida")
    return _ask(
        f"Kanal a'zosi shu savolni berdi: '{question}'\n\n"
        f"Savolga {lang} javob ber. Aniq, to'liq va foydali bo'lsin. "
        f"Telegram markdown formatida."
    )


def generate_weekly_plan() -> str:
    lang = LANGUAGE_NAMES.get(CHANNEL_LANGUAGE, "o'zbek tilida")
    return _ask(
        f"'{CHANNEL_TOPIC}' Telegram kanali uchun 1 haftalik kontent rejasini tuz. "
        f"Har kun uchun 2-3 ta post mavzusi taklif qil. "
        f"Reja {lang} bo'lsin. Markdown formatida."
    )
