import asyncio

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from core import database as db
from core.crypto import decrypt_token
from mirror.router import router as mirror_router


class MirrorManager:
    def __init__(self):
        self._running = {}

    def is_running(self, owner_id):
        return owner_id in self._running

    async def start_mirror(self, owner_id, token):
        if owner_id in self._running:
            return

        bot = Bot(token=token)
        dp = Dispatcher(storage=MemoryStorage())
        dp.include_router(mirror_router)

        task = asyncio.create_task(self._run(bot, dp, owner_id))
        self._running[owner_id] = {"bot": bot, "dp": dp, "task": task}

    async def _run(self, bot, dp, owner_id):
        try:
            await bot.delete_webhook(drop_pending_updates=True)
            await dp.start_polling(bot)
        except Exception:
            pass
        finally:
            self._running.pop(owner_id, None)

    async def stop_mirror(self, owner_id):
        entry = self._running.pop(owner_id, None)
        if not entry:
            return

        entry["task"].cancel()
        try:
            await entry["task"]
        except Exception:
            pass

        try:
            await entry["bot"].session.close()
        except Exception:
            pass

    async def start_all(self):
        mirrors = await db.get_all_active_mirrors()
        for row in mirrors:
            token = decrypt_token(row["token_encrypted"])
            await self.start_mirror(row["owner_id"], token)

    async def stop_all(self):
        for owner_id in list(self._running.keys()):
            await self.stop_mirror(owner_id)


mirror_manager = MirrorManager()
