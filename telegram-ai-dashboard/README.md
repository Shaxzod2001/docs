# 🤖 Telegram AI Dashboard

Kompyuteringizda (localhost) ishlaydigan veb admin panel orqali Telegram
kanalingizni AI yordamida boshqaring.

## ✨ Imkoniyatlar

- **🤖 AI postlar** — Groq (Llama) bilan kreativ postlar yaratish
- **📅 Rejalashtirish** — postlarni belgilangan vaqtda avtomatik joylash
- **⏰ Avtomatik post** — har kuni belgilangan vaqtlarda AI o'zi post yozadi
- **👥 Obunachilar** — obunachilar ro'yxatini ko'rish va nazorat qilish
- **🎯 Qiziqishlar** — obunachilar izohlarini AI bilan tahlil qilib, qiziqishlarini aniqlash
- **📈 Statistika** — obunachilar o'sishi, post ko'rishlari, reaksiyalar (grafiklar bilan)

## 🔀 Ikki rejim

| | 🤖 BOT REJIMI (oson) | 👤 TO'LIQ REJIM |
|---|---|---|
| Kerak | Bot token (@BotFather) | API_ID/HASH (my.telegram.org) |
| AI postlar | ✅ | ✅ |
| Rejalashtirish / avto | ✅ | ✅ |
| Obunachilar soni + grafik | ✅ | ✅ |
| Qiziqishlar (izoh yozganlar) | ✅ jonli kuzatuv | ✅ tarix bilan |
| To'liq obunachilar ro'yxati | ❌ | ✅ |

> Tavsiya: **BOT REJIMI** bilan boshlang — eng oson. `.env` da `TELEGRAM_API_ID`/`HASH`
> bo'sh qolsa, dastur avtomatik bot rejimida ishlaydi.

## 🛠 O'rnatish (BOT REJIMI)

### 1. Kerakli narsalar
- Python 3.10+
- Telegram bot (siz kanalga **admin** qilib qo'shgan)

### 2. Kalitlarni olish

**Bot token** (@BotFather):
1. Telegram'da @BotFather ga yozing → `/newbot` (yoki mavjud botingiz)
2. Tokenni nusxalang
3. Botni kanalingizga **admin** qilib qo'shing (post yuborishi uchun)

**Groq API** (bepul):
1. https://console.groq.com → "API Keys" → "Create API Key"
2. Kalitni nusxalang (`gsk_...`)

### 3. Sozlash

```bash
cd telegram-ai-dashboard
pip install -r requirements.txt
copy .env.example .env      # Windows (Linux/Mac: cp .env.example .env)
notepad .env                # kalitlarni kiriting
```

`.env` da to'ldiring: `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHANNEL`, `GROQ_API_KEY`.
(`TELEGRAM_API_ID`/`HASH` ni **bo'sh** qoldiring — bot rejimi uchun.)

### 4. Ishga tushirish

```bash
python app.py
```

Brauzerda oching: **http://127.0.0.1:8000**

## 🛠 TO'LIQ REJIM (ixtiyoriy, keyinroq)

To'liq obunachilar ro'yxati kerak bo'lsa, `.env` ga `TELEGRAM_API_ID`,
`TELEGRAM_API_HASH`, `TELEGRAM_PHONE` qo'shing (my.telegram.org dan), so'ng:

```bash
python login.py     # telefon kodini bir marta kiriting
python app.py
```

## 📌 Eslatmalar

- **Bot rejimida** qiziqishlarni aniqlash uchun: bot kanalga bog'langan
  **muhokama guruhiga** admin qilib qo'shilishi va @BotFather'da privacy
  o'chirilishi kerak (`/setprivacy` → **Disable**). Shundan keyin obunachilar
  yozgan izohlar to'planib boradi.
- Bot rejimida post **ko'rishlar soni** Telegram tomonidan berilmaydi (faqat
  to'liq rejimda mavjud).
- `.env` va `*.session` fayllari maxfiy — hech kimga bermang, GitHub'ga yuklamang.

## ⚠️ Xavfsizlik

Bu dastur sizning Telegram akkauntingiz nomidan ishlaydi (user akkaunt).
Faqat o'z kanalingiz uchun ishlating. Sessiya fayli (`*.session`) parol kabi —
uni himoyalang.
