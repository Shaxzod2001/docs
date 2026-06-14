#!/usr/bin/env python3
"""Telegram AI Dashboard - FastAPI veb server."""
import logging
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request
from pydantic import BaseModel

import database as db
import ai_engine
import services
import telegram_client as tg
from scheduler import setup_scheduler, stop_scheduler
from config import (
    WEB_HOST, WEB_PORT, CHANNEL_TOPIC, CHANNEL, GROQ_MODEL, AUTO_POST_TIMES,
)

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await db.init_db()
    setup_scheduler()
    logger.info(f"Dashboard ishga tushdi: http://{WEB_HOST}:{WEB_PORT}")
    yield
    stop_scheduler()


app = FastAPI(title="Telegram AI Dashboard", lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


# ---------- Modellar ----------

class GenerateRequest(BaseModel):
    topic: str | None = None


class CreatePostRequest(BaseModel):
    content: str
    scheduled_time: str | None = None  # "YYYY-MM-DD HH:MM"
    send_now: bool = False


# ---------- Sahifa ----------

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "channel": CHANNEL,
        "topic": CHANNEL_TOPIC,
        "model": GROQ_MODEL,
    })


# ---------- API: holat ----------

@app.get("/api/status")
async def api_status():
    authorized = await tg.is_authorized()
    return {
        "telegram_authorized": authorized,
        "channel": CHANNEL,
        "topic": CHANNEL_TOPIC,
        "model": GROQ_MODEL,
        "auto_post_times": AUTO_POST_TIMES,
    }


# ---------- API: dashboard ----------

@app.get("/api/dashboard")
async def api_dashboard():
    snapshots = await db.get_stat_snapshots(limit=60)
    sub_count = await db.count_subscribers()
    sent_posts = await db.get_posts(status="sent", limit=10)
    scheduled = await db.get_posts(status="scheduled", limit=50)

    latest_count = snapshots[-1]["subscriber_count"] if snapshots else sub_count
    total_views = sum(p.get("views", 0) for p in sent_posts)
    total_reactions = sum(p.get("reactions", 0) for p in sent_posts)

    return {
        "subscriber_count": latest_count,
        "tracked_subscribers": sub_count,
        "scheduled_count": len(scheduled),
        "total_views": total_views,
        "total_reactions": total_reactions,
        "snapshots": snapshots,
        "top_posts": sorted(sent_posts, key=lambda p: p.get("views", 0), reverse=True)[:5],
    }


# ---------- API: postlar ----------

@app.get("/api/posts")
async def api_posts():
    return {"posts": await db.get_posts(limit=100)}


@app.post("/api/posts/generate")
async def api_generate(req: GenerateRequest):
    try:
        content = ai_engine.generate_post(topic=req.topic)
        return {"content": content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/posts/ideas")
async def api_ideas():
    try:
        return {"ideas": ai_engine.generate_post_ideas()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/posts")
async def api_create_post(req: CreatePostRequest):
    try:
        if req.send_now:
            result = await services.send_post_now(req.content, source="manual")
            return {"status": "sent", **result}

        if req.scheduled_time:
            scheduled = datetime.strptime(req.scheduled_time, "%Y-%m-%d %H:%M")
            if scheduled <= datetime.now():
                raise HTTPException(status_code=400, detail="Vaqt o'tib ketgan.")
            post_id = await db.add_post(
                req.content, status="scheduled", scheduled_time=scheduled)
            return {"status": "scheduled", "post_id": post_id}

        post_id = await db.add_post(req.content, status="draft")
        return {"status": "draft", "post_id": post_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/posts/{post_id}/send")
async def api_send_post(post_id: int):
    post = await db.get_post(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post topilmadi.")
    try:
        message_id = await tg.send_post(post["content"])
        await db.mark_post_sent(post_id, message_id)
        return {"status": "sent", "message_id": message_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/posts/{post_id}")
async def api_delete_post(post_id: int):
    deleted = await db.delete_post(post_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Post topilmadi.")
    return {"status": "deleted"}


# ---------- API: obunachilar ----------

@app.get("/api/subscribers")
async def api_subscribers():
    subs = await db.get_subscribers()
    with_interests = [s for s in subs if s.get("interests")]
    return {"subscribers": subs, "with_interests": len(with_interests)}


@app.post("/api/subscribers/sync")
async def api_sync_subscribers():
    try:
        return await services.sync_subscribers()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/subscribers/analyze")
async def api_analyze_interests():
    try:
        result = await services.analyze_interests()
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/subscribers/insights")
async def api_insights():
    subs = await db.get_subscribers()
    interests = [s["interests"] for s in subs if s.get("interests")]
    if not interests:
        return {"analysis": "Hali qiziqishlar aniqlanmagan. Avval tahlilni ishga tushiring."}
    try:
        return {"analysis": ai_engine.analyze_audience(interests)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------- API: statistika sync ----------

@app.post("/api/sync")
async def api_sync():
    try:
        return await services.sync_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=WEB_HOST, port=WEB_PORT)
