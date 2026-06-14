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


def _parse_rich(raw):
    image_prompt = ""
    content = raw.strip()
    if "POST:" in raw:
        head, _, body = raw.partition("POST:")
        content = body.strip()
        for line in head.splitlines():
            if line.strip().upper().startswith("IMAGE:"):
                image_prompt = line.split(":", 1)[1].strip()
    else:
        lines = raw.splitlines()
        if lines and lines[0].strip().upper().startswith("IMAGE:"):
            image_prompt = lines[0].split(":", 1)[1].strip()
            content = "\n".join(lines[1:]).strip()
    if not image_prompt:
        image_prompt = f"{CHANNEL_TOPIC}, modern digital illustration, vibrant colors"
    return {"content": content[:1000], "image_prompt": image_prompt}


def generate_rich_post(topic=None, style="kreativ"):
    """Rasm tavsifi + jonli emojili post matnini birga yaratadi."""
    lang = _lang()
    system = (
        "Sen professional SMM kontent-menejersan. Telegram kanal uchun jonli, "
        "mos emojilar bilan bezatilgan, qiziqarli postlar yozasan. "
        "Javobni ANIQ quyidagi formatda ber, boshqa hech narsa qo'shma:\n"
        "IMAGE: <ingliz tilida rasm uchun qisqa, aniq, jonli tavsif>\n"
        "POST:\n<post matni>"
    )
    if topic:
        topic_line = f"Mavzu: {topic}."
    else:
        topic_line = f"'{CHANNEL_TOPIC}' yo'nalishida o'zing qiziqarli mavzu tanla."
    user = (
        f"{topic_line}\n"
        f"Post {lang} bo'lsin. Ko'p mos emoji ishlat, diqqatni tortuvchi hook bilan "
        f"boshla, foydali ma'lumot ber, oxirida savol yoki harakatga chaqiriq (CTA) qo'sh. "
        f"MUHIM: post matni 700 belgidan oshmasin (rasm tagiga sig'ishi kerak)."
    )
    raw = _chat(system, user, max_tokens=800, temperature=0.9)
    return _parse_rich(raw)


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
