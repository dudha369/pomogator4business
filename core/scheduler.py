import asyncio
import logging
from datetime import date, datetime

from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError

from core import database as db
from modules.story import autopost_tick

_CHECK_INTERVAL = 3600

logger = logging.getLogger("bot.scheduler")


async def run(bot):
    while True:
        try:
            await autopost_tick(bot, date.today().isoformat())
        except Exception:
            pass
        await asyncio.sleep(_CHECK_INTERVAL)


async def emoji_clock_tick(bot):
    time_key = datetime.now().strftime("%H:%M")
    custom_emoji_id = await db.get_clock_emoji(time_key)
    if not custom_emoji_id:
        return

    owners = await db.get_active_emoji_status_owners()
    for owner_id in owners:
        try:
            await bot.set_user_emoji_status(
                user_id=owner_id,
                emoji_status_custom_emoji_id=custom_emoji_id,
            )
        except (TelegramBadRequest, TelegramForbiddenError):
            # Реального способа "спросить" у Telegram, дан ли доступ, нет —
            # единственный надёжный сигнал это факт неудачи самого вызова.
            # Раз сюда попали при granted=True, значит доступ отозван
            # где-то на стороне Telegram (владелец сам его выключил) — чиним
            # свою же БД, а не тихо продолжаем биться в закрытую дверь
            # каждую минуту.
            logger.warning(
                "Доступ к эмодзи-статусу отозван для owner_id=%s — выключаю", owner_id
            )
            await db.set_emoji_status_granted(owner_id, False)
            await db.set_emoji_status_enabled(owner_id, False)
            try:
                await bot.send_message(
                    chat_id=owner_id,
                    text=(
                        "⚠️ Доступ к эмодзи-статусу отозван — часы в статусе "
                        "выключены. Чтобы включить заново, откройте мини-приложение "
                        "→ Аккаунт и разрешите доступ ещё раз."
                    ),
                )
            except Exception:
                pass
        except Exception:
            pass


async def run_emoji_clock(bot):
    while True:
        now = datetime.now()
        sleep_for = 60 - now.second - now.microsecond / 1_000_000
        await asyncio.sleep(max(0.0, sleep_for))
        try:
            await emoji_clock_tick(bot)
        except Exception:
            pass
