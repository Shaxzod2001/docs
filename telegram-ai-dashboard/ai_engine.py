import requests
from config import GROQ_API_KEY, GROQ_MODEL, CHANNEL_TOPIC, CHANNEL_LANGUAGE

LANG = {
    "uz": "o'zbek tilida",
    "ru": "rus tilida",
    "en": "ingliz tilida",
}


def _lang():
    return LANG.get(CHANNEL_LANGUAGE, "o'zbek tilida")


def _chat(system, user, max_tokens=1024, temperature=0.8):
    if not GROQ_API_KEY:
        raise RuntimeError("GROQ_API_KEY o'rnatilmagan. .env faylga qo'shing.")
    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": GROQ_MODEL,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "max_tokens": max_tokens,
            "temperature": temperature,
        },
        timeout=40,
    )
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"].strip()


def generate_post(topic=None, style="kreativ"):
    lang = _lang()
    system = (
        "Sen professional SMM kontent-menejersan. Telegram kanal uchun "
        "kreativ, qiziqarli va o'qishga oson postlar yozasan. "
        "Markdown formatlash va mos emoji ishlat. Postni darhol matn bilan boshla, "
        "izoh yoki kirish so'zlarsiz."
    )
    if topic:
        user = (
            f"'{topic}' mavzusida {lang} {style} Telegram post yoz. "
            f"Diqqatni tortuvchi hook bilan boshla, foydali ma'lumot ber, "
            f"oxirida obunachilarga savol yoki harakatga chaqiriq (CTA) qo'sh. "
            f"150-350 so'z."
        )
    else:
        user = (
            f"'{CHANNEL_TOPIC}' kanali uchun {lang} {style} Telegram post yoz. "
            f"O'zing qiziqarli mavzu tanla. Hook, foydali ma'lumot va CTA bo'lsin. "
            f"150-350 so'z."
        )
    return _chat(system, user, temperature=0.9)


def generate_post_ideas(count=5):
    lang = _lang()
    system = "Sen kontent-strateg ekspertisan."
    user = (
        f"'{CHANNEL_TOPIC}' Telegram kanali uchun {count} ta qiziqarli post g'oyasini "
        f"{lang} taklif qil. Har birini bitta qisqa qatorda, raqamlangan ro'yxat ko'rinishida ber."
    )
    return _chat(system, user, max_tokens=400, temperature=0.9)


def detect_interests(messages):
    if not messages:
        return ""
    text = "\n".join(messages)[:3500]
    system = "Sen foydalanuvchi qiziqishlarini aniqlovchi aniq tahlilchisan."
    user = (
        "Quyidagi foydalanuvchi xabarlari asosida uning 3-5 ta asosiy qiziqishini "
        "aniqla. FAQAT vergul bilan ajratilgan qisqa ro'yxat ber, boshqa hech narsa yozma.\n\n"
        f"Xabarlar:\n{text}"
    )
    return _chat(system, user, max_tokens=80, temperature=0.3)


def analyze_audience(interests_list):
    if not interests_list:
        return "Tahlil uchun yetarli ma'lumot yo'q."
    joined = "; ".join(interests_list)[:3500]
    lang = _lang()
    system = "Sen auditoriya tahlili bo'yicha ekspertsan."
    user = (
        f"Quyida kanal obunachilarining aniqlangan qiziqishlari berilgan. "
        f"Ularni {lang} tahlil qil: 1) eng ommabop qiziqishlar, "
        f"2) auditoriya uchun qanday kontent yaratish kerakligi bo'yicha 3-4 ta tavsiya. "
        f"Qisqa va aniq.\n\nQiziqishlar:\n{joined}"
    )
    return _chat(system, user, max_tokens=600, temperature=0.6)
