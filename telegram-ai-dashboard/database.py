import aiosqlite
from datetime import datetime
from config import DATABASE_PATH


async def init_db():
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'draft',
                source TEXT DEFAULT 'manual',
                scheduled_time TEXT,
                sent_time TEXT,
                message_id INTEGER,
                views INTEGER DEFAULT 0,
                reactions INTEGER DEFAULT 0,
                created_at TEXT NOT NULL
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS subscribers (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                is_bot INTEGER DEFAULT 0,
                interests TEXT,
                message_count INTEGER DEFAULT 0,
                first_seen TEXT,
                last_updated TEXT
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS stats_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                subscriber_count INTEGER NOT NULL
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                username TEXT,
                first_name TEXT,
                text TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)
        await db.commit()


# ---------- POSTS ----------

async def add_post(content, status="draft", source="manual", scheduled_time=None):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cur = await db.execute(
            """INSERT INTO posts (content, status, source, scheduled_time, created_at)
               VALUES (?, ?, ?, ?, ?)""",
            (content, status, source,
             scheduled_time.isoformat() if scheduled_time else None,
             datetime.now().isoformat()),
        )
        await db.commit()
        return cur.lastrowid


async def get_posts(status=None, limit=100):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        if status:
            cur = await db.execute(
                "SELECT * FROM posts WHERE status = ? ORDER BY id DESC LIMIT ?",
                (status, limit))
        else:
            cur = await db.execute(
                "SELECT * FROM posts ORDER BY id DESC LIMIT ?", (limit,))
        rows = await cur.fetchall()
        return [dict(r) for r in rows]


async def get_post(post_id):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("SELECT * FROM posts WHERE id = ?", (post_id,))
        row = await cur.fetchone()
        return dict(row) if row else None


async def get_due_posts():
    now = datetime.now().isoformat()
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute(
            "SELECT * FROM posts WHERE status = 'scheduled' AND scheduled_time <= ?",
            (now,))
        rows = await cur.fetchall()
        return [dict(r) for r in rows]


async def mark_post_sent(post_id, message_id):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            "UPDATE posts SET status='sent', sent_time=?, message_id=? WHERE id=?",
            (datetime.now().isoformat(), message_id, post_id))
        await db.commit()


async def update_post_metrics(message_id, views, reactions):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            "UPDATE posts SET views=?, reactions=? WHERE message_id=?",
            (views, reactions, message_id))
        await db.commit()


async def delete_post(post_id):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cur = await db.execute("DELETE FROM posts WHERE id = ?", (post_id,))
        await db.commit()
        return cur.rowcount > 0


# ---------- SUBSCRIBERS ----------

async def upsert_subscriber(user_id, username, first_name, is_bot=False):
    now = datetime.now().isoformat()
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("""
            INSERT INTO subscribers (user_id, username, first_name, is_bot, first_seen, last_updated)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                username=excluded.username,
                first_name=excluded.first_name,
                last_updated=excluded.last_updated
        """, (user_id, username, first_name, 1 if is_bot else 0, now, now))
        await db.commit()


async def set_subscriber_interests(user_id, interests, message_count):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            "UPDATE subscribers SET interests=?, message_count=?, last_updated=? WHERE user_id=?",
            (interests, message_count, datetime.now().isoformat(), user_id))
        await db.commit()


async def get_subscribers(limit=1000):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute(
            "SELECT * FROM subscribers ORDER BY message_count DESC, last_updated DESC LIMIT ?",
            (limit,))
        rows = await cur.fetchall()
        return [dict(r) for r in rows]


async def count_subscribers():
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cur = await db.execute("SELECT COUNT(*) FROM subscribers WHERE is_bot=0")
        row = await cur.fetchone()
        return row[0] if row else 0


# ---------- STATS ----------

async def add_stat_snapshot(subscriber_count):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            "INSERT INTO stats_snapshots (timestamp, subscriber_count) VALUES (?, ?)",
            (datetime.now().isoformat(), subscriber_count))
        await db.commit()


async def get_stat_snapshots(limit=60):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute(
            "SELECT * FROM stats_snapshots ORDER BY id DESC LIMIT ?", (limit,))
        rows = await cur.fetchall()
        return list(reversed([dict(r) for r in rows]))


# ---------- COMMENTS (bot rejimi) ----------

async def add_comment(user_id, username, first_name, text):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            "INSERT INTO comments (user_id, username, first_name, text, created_at) "
            "VALUES (?, ?, ?, ?, ?)",
            (user_id, username, first_name, text, datetime.now().isoformat()))
        await db.commit()


async def get_comments_grouped(min_count=2, max_users=40):
    """Foydalanuvchi bo'yicha guruhlangan izoh matnlari."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute(
            "SELECT user_id, text FROM comments ORDER BY id DESC LIMIT 5000")
        rows = await cur.fetchall()

    grouped = {}
    for r in rows:
        grouped.setdefault(r["user_id"], []).append(r["text"])

    ranked = sorted(grouped.items(), key=lambda kv: len(kv[1]), reverse=True)
    return {uid: msgs for uid, msgs in ranked[:max_users] if len(msgs) >= min_count}


# ---------- SETTINGS ----------

async def get_setting(key, default=None):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cur = await db.execute("SELECT value FROM settings WHERE key = ?", (key,))
        row = await cur.fetchone()
        return row[0] if row else default


async def set_setting(key, value):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            "INSERT INTO settings (key, value) VALUES (?, ?) "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            (key, str(value)))
        await db.commit()
