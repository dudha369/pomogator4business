from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from handlers.business_messages import router as business_messages_router
from handlers.connection import router as connection_router
from handlers.emoji_status import router as emoji_status_router
from handlers.games import router as games_router
from handlers.mirror import router as mirror_router
from handlers.settings import router as settings_router
from modules.archive import router as archive_router

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())


def setup_routes() -> Dispatcher:
    dp.include_router(connection_router)
    dp.include_router(business_messages_router)
    dp.include_router(archive_router)
    dp.include_router(mirror_router)
    dp.include_router(emoji_status_router)
    dp.include_router(games_router)
    dp.include_router(settings_router)

    return dp
