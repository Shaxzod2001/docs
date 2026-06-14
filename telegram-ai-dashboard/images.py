"""Bepul AI rasm generatori (Pollinations.ai) bilan ishlash."""
import random
from urllib.parse import quote

import requests


STYLE_SUFFIX = (
    "professional, clean, modern, corporate, high quality, "
    "minimalist, sharp focus, no text, no watermark"
)


def build_image_url(prompt, seed=None):
    """Pollinations.ai rasm URL manzilini yasaydi (kalit kerak emas)."""
    if seed is None:
        seed = random.randint(1, 1_000_000)
    full = f"{(prompt or 'technology').strip()[:240]}, {STYLE_SUFFIX}"
    safe = quote(full)
    return (
        f"https://image.pollinations.ai/prompt/{safe}"
        f"?width=1024&height=576&nologo=true&seed={seed}&referrer=tg-dashboard"
    )


def fetch_image(url):
    """URL bo'yicha rasmni yuklab oladi (baytlar). Xato bo'lsa None."""
    headers = {"User-Agent": "Mozilla/5.0 (tg-dashboard)"}
    for attempt in range(2):
        try:
            r = requests.get(url, timeout=150, headers=headers)
            ctype = r.headers.get("content-type", "")
            if r.ok and r.content and ctype.startswith("image"):
                return r.content
        except Exception:
            pass
    return None
