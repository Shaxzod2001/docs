# Telegram Kanal AI Agenti

Ta'lim Telegram kanallarini avtomatik boshqarish uchun AI agent.

## Imkoniyatlar

- **AI kontent yaratish** — Claude AI yordamida kanal uchun postlar yaratish
- **Jadval bo'yicha yuborish** — Postlarni kerakli vaqtga rejalashtirish
- **Yangiliklar yig'ish** — RSS manbalardan yangilik olib, post yaratish
- **Savollarga javob** — Kanal a'zolarining savollariga AI bilan javob berish

## O'rnatish

### 1. Loyihani yuklang

```bash
git clone <repo-url>
cd telegram-ai-agent
```

### 2. Virtual muhit yarating

```bash
python -m venv venv
source venv/bin/activate   # Linux/Mac
# yoki
venv\Scripts\activate      # Windows
```

### 3. Kutubxonalarni o'rnating

```bash
pip install -r requirements.txt
```

### 4. Muhit o'zgaruvchilarini sozlang

```bash
cp .env.example .env
```

`.env` faylini oching va quyidagilarni to'ldiring:

| O'zgaruvchi | Tavsif |
|---|---|
| `TELEGRAM_BOT_TOKEN` | [@BotFather](https://t.me/BotFather) dan oling |
| `TELEGRAM_CHANNEL_ID` | Kanalingiz username yoki ID si |
| `ANTHROPIC_API_KEY` | [console.anthropic.com](https://console.anthropic.com) dan oling |
| `ADMIN_USER_IDS` | Sizning Telegram ID ingiz |
| `CHANNEL_TOPIC` | Kanal mavzusi |
| `CHANNEL_LANGUAGE` | `uz` / `ru` / `en` |

### 5. Botni ishga tushiring

```bash
python agent.py
```

## Admin buyruqlari

| Buyruq | Tavsif |
|---|---|
| `/start` | Botni ishga tushirish |
| `/post [mavzu]` | Yangi post yaratish |
| `/news` | Yangiliklar asosida post |
| `/schedule YYYY-MM-DD HH:MM matn` | Post rejalashtirish |
| `/list` | Rejalashtirilgan postlar ro'yxati |
| `/plan` | Haftalik kontent rejasi |
| `/stats` | Statistika |

## Avtomatik jadval

Bot har kuni avtomatik ravishda post yuboradi:
- **09:00** — Ertalabki ta'lim posti
- **14:00** — Yangiliklar asosida post
- **18:00** — Kechki ta'lim posti

## Telegram ID ni aniqlash

Telegram ID ingizni bilish uchun [@userinfobot](https://t.me/userinfobot) ga `/start` yuboring.

## Kanal ID si

- **Username**: `@mening_kanalim` — to'g'ridan-to'g'ri ishlating
- **Raqamli ID**: Bot kanalga admin sifatida qo'shilgandan keyin `/stats` orqali aniqlang
