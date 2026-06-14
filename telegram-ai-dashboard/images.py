"""Bepul AI rasm generatori (Pollinations.ai) bilan ishlash."""
import random
from urllib.parse import quote

import requests


def build_image_url(prompt, seed=None):
    """Pollinations.ai rasm URL manzilini yasaydi (kalit kerak emas)."""
    if seed is None:
        seed = random.randint(1, 1_000_000)
    safe = quote((prompt or "technology").strip()[:300])
    return (
        f"https://image.pollinations.ai/prompt/{safe}"
        f"?width=1024&height=576&nologo=true&seed={seed}&model=flux"
    )


def fetch_image(url):
    """URL bo'yicha rasmni yuklab oladi (baytlar). Xato bo'lsa None."""
    try:
        r = requests.get(url, timeout=120)
        ctype = r.headers.get("content-type", "")
        if r.ok and r.content and ctype.startswith("image"):
            return r.content
    except Exception:
        pass
    return None
