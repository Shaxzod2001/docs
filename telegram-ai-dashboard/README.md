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

## 🛠 O'rnatish

### 1. Kerakli narsalar
- Python 3.10+
- Telegram akkaunt (kanalga admin/egasi)

### 2. Kalitlarni olish

**Telegram API** (my.telegram.org):
1. https://my.telegram.org ga kiring
2. "API development tools" → yangi app yarating
3. `api_id` va `api_hash` ni nusxalang

**Groq API** (bepul):
1. https://console.groq.com ga kiring
2. "API Keys" → "Create API Key"
3. Kalitni nusxalang (`gsk_...`)

### 3. Sozlash

```bash
cd telegram-ai-dashboard
pip install -r requirements.txt
cp .env.example .env
```

`.env` faylni tahrirlang va kalitlaringizni kiriting (TELEGRAM_API_ID,
TELEGRAM_API_HASH, TELEGRAM_PHONE, TELEGRAM_CHANNEL, GROQ_API_KEY).

### 4. Telegramga bir marta kirish

```bash
python login.py
```

Telefoningizga kelgan kodni kiriting. Sessiya fayli saqlanadi
(keyingi safar kerak emas).

### 5. Dashboardni ishga tushirish

```bash
python app.py
```

Brauzerda oching: **http://127.0.0.1:8000**

## 📌 Eslatmalar

- **Obunachilar ro'yxati** va **qiziqishlar** uchun siz kanal admini bo'lishingiz kerak.
- **Qiziqishlarni aniqlash** kanalga bog'langan **muhokama guruhi** (izohlar) bo'lganda ishlaydi.
- `.env` va `*.session` fayllari maxfiy — hech kimga bermang, GitHub'ga yuklamang.

## ⚠️ Xavfsizlik

Bu dastur sizning Telegram akkauntingiz nomidan ishlaydi (user akkaunt).
Faqat o'z kanalingiz uchun ishlating. Sessiya fayli (`*.session`) parol kabi —
uni himoyalang.
