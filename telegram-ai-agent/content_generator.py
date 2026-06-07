import google.generativeai as genai
from config import GEMINI_API_KEY, CHANNEL_TOPIC, CHANNEL_LANGUAGE

_model = None


def get_model():
    global _model
    if _model is None:
        genai.configure(api_key=GEMINI_API_KEY)
        _model = genai.GenerativeModel(
            model_name="gemini-2.0-flash",
            system_instruction=(
                "Sen ta'lim kanali uchun kontent yaratuvchi AI agentsan. "
                "Qiziqarli va foydali ta'lim postlari yoz. "
                "Emoji va Telegram markdown formatlashdan foydalan. "
                "Har doim ijobiy va rag'batlantiruvchi ton ushlab tur."
            ),
        )
    return _model


LANGUAGE_NAMES = {
    "uz": "o'zbek tilida",
    "ru": "rus tilida",
    "en": "ingliz tilida",
}


def generate_post(topic: str | None = None, custom_prompt: str | None = None) -> str:
    model = get_model()
    lang = LANGUAGE_NAMES.get(CHANNEL_LANGUAGE, "o'zbek tilida")

    if custom_prompt:
        prompt = f"{custom_prompt}\n\nJavobni {lang} yozing."
    elif topic:
        prompt = (
            f"'{topic}' mavzusida Telegram kanal posti yoz. "
            f"Post {lang} bo'lsin. "
            f"Post qiziqarli, foydali va ta'limiy bo'lsin. "
            f"Emoji ishlatish mumkin. 200-400 so'z bo'lsin."
        )
    else:
        prompt = (
            f"'{CHANNEL_TOPIC}' kanali uchun bugun yangi ta'limiy post yoz. "
            f"Post {lang} bo'lsin. "
            f"Mavzu tanlang va qiziqarli ma'lumot bering. "
            f"Emoji ishlatish mumkin. 200-400 so'z bo'lsin."
        )

    response = model.generate_content(prompt)
    return response.text


def generate_post_from_news(news_title: str, news_summary: str) -> str:
    model = get_model()
    lang = LANGUAGE_NAMES.get(CHANNEL_LANGUAGE, "o'zbek tilida")

    prompt = (
        f"Quyidagi yangilik asosida Telegram kanal posti yoz:\n\n"
        f"Sarlavha: {news_title}\n"
        f"Qisqacha: {news_summary}\n\n"
        f"Post {lang} bo'lsin. "
        f"Ta'limiy va rag'batlantiruvchi tarzda yoz. "
        f"Emoji ishlatish mumkin. 150-300 so'z bo'lsin."
    )

    response = model.generate_content(prompt)
    return response.text


def answer_question(question: str) -> str:
    model = get_model()
    lang = LANGUAGE_NAMES.get(CHANNEL_LANGUAGE, "o'zbek tilida")

    prompt = (
        f"Kanal a'zosi shu savolni berdi: '{question}'\n\n"
        f"Savolga {lang} javob ber. "
        f"Javob aniq, to'liq va foydali bo'lsin. "
        f"Telegram markdown formatida yoz."
    )

    response = model.generate_content(prompt)
    return response.text


def generate_weekly_plan() -> str:
    model = get_model()
    lang = LANGUAGE_NAMES.get(CHANNEL_LANGUAGE, "o'zbek tilida")

    prompt = (
        f"'{CHANNEL_TOPIC}' Telegram kanali uchun 1 haftalik kontent rejasini tuz. "
        f"Har kun uchun 2-3 ta post mavzusi taklif qil. "
        f"Reja {lang} bo'lsin. "
        f"Markdown formatida chiroyli qilib yoz."
    )

    response = model.generate_content(prompt)
    return response.text
