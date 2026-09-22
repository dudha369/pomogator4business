import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Header, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from tortoise import Tortoise

from api.routes import router as api_router
from bot_instance import bot, dp
from config import CORS_ORIGINS, TORTOISE_ORM, WEBHOOK_PATH, WEBHOOK_SECRET, WEBHOOK_URL
from core.loader import load_modules
from core.mirror_manager import mirror_manager
from core.scheduler import run as run_story_scheduler
from core.scheduler import run_emoji_clock

_background_tasks: list[asyncio.Task] = []


@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.basicConfig(level=logging.INFO)

    load_modules()
    await Tortoise.init(config=TORTOISE_ORM, _enable_global_fallback=True)

    if WEBHOOK_URL:
        await bot.set_webhook(
            url=WEBHOOK_URL,
            secret_token=WEBHOOK_SECRET,
            drop_pending_updates=True,
        )
    else:
        logging.warning("WEBHOOK_BASE_URL не задан — вебхук не установлен")

    _background_tasks.append(asyncio.create_task(run_story_scheduler(bot)))
    _background_tasks.append(asyncio.create_task(run_emoji_clock(bot)))
    _background_tasks.append(asyncio.create_task(mirror_manager.start_all()))

    yield

    for task in _background_tasks:
        task.cancel()
    for task in _background_tasks:
        try:
            await task
        except (Exception, asyncio.CancelledError):
            pass

    await mirror_manager.stop_all()
    await bot.session.close()
    await Tortoise.close_connections()


app = FastAPI(lifespan=lifespan)

if CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_ORIGINS,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix="/api")


@app.post(WEBHOOK_PATH)
async def telegram_webhook(
    request: Request,
    x_telegram_bot_api_secret_token: str = Header(default=None),
):
    if x_telegram_bot_api_secret_token != WEBHOOK_SECRET:
        raise HTTPException(status_code=401, detail="Invalid secret token")

    data = await request.json()
    await dp.feed_webhook_update(bot, data)
    return Response(status_code=200)


@app.get("/health")
async def health():
    return {"status": "ok"}
