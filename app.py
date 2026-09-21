import asyncio
import logging
from contextlib import asynccontextmanager

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from fastapi import FastAPI, Header, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from api.routes import router as api_router
from config import (
    BOT_TOKEN,
    CORS_ORIGINS,
    WEBHOOK_PATH,
    WEBHOOK_SECRET,
    WEBHOOK_URL,
    API_HOST,
    API_PORT,
)
from core.database import init_db
from core.loader import load_modules
from core.mirror_manager import mirror_manager
from core.scheduler import run as run_story_scheduler
from core.scheduler import run_emoji_clock
from handlers.business_messages import router as business_messages_router
from handlers.connection import router as connection_router
from handlers.emoji_status import router as emoji_status_router
from handlers.games import router as games_router
from handlers.mirror import router as mirror_router
from handlers.settings import router as settings_router
from modules.archive import router as archive_router

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())

dp.include_router(connection_router)
dp.include_router(business_messages_router)
dp.include_router(archive_router)
dp.include_router(mirror_router)
dp.include_router(emoji_status_router)
dp.include_router(games_router)
dp.include_router(settings_router)

_background_tasks = []


@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.basicConfig(level=logging.INFO)

    load_modules()
    await init_db()

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

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=API_HOST, port=API_PORT)
