import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aiogram import Bot
from aiogram.exceptions import TelegramRetryAfter
from aiogram.types import BufferedInputFile, InputSticker
from tortoise import Tortoise

from config import BOT_TOKEN, TORTOISE_ORM
from core import database as db

INPUT_DIR = "assets/generated_emoji"
PACK_SIZE = 180
PACK_COUNT = 8
EMOJI_LIST = ["🕐"]
UPLOAD_DELAY = 1.0

ADMIN_USER_ID = 1218892156


def all_time_keys():
    return [f"{h:02d}:{m:02d}" for h in range(24) for m in range(60)]


def _read_sticker_bytes(pack_index, time_key):
    path = os.path.join(
        INPUT_DIR, f"pack_{pack_index}", f"{time_key.replace(':', '-')}.png"
    )
    with open(path, "rb") as f:
        return f.read()


def _build_input_sticker(pack_index, time_key):
    data = _read_sticker_bytes(pack_index, time_key)
    return InputSticker(
        sticker=BufferedInputFile(data, filename=f"{time_key}.png"),
        format="static",
        emoji_list=EMOJI_LIST,
    )


async def _call_with_retry(coro_factory):
    while True:
        try:
            return await coro_factory()
        except TelegramRetryAfter as exc:
            await asyncio.sleep(exc.retry_after + 1)


async def _upload_pack(bot, me, pack_index, chunk):
    pack_row = await db.get_clock_pack(pack_index)
    pack_name = f"clock{pack_index}_by_{me.username.lower()}"
    uploaded_count = pack_row["uploaded_count"] if pack_row else 0

    if uploaded_count == 0:
        first_batch = chunk[:50]
        stickers = [_build_input_sticker(pack_index, t) for t in first_batch]

        await _call_with_retry(
            lambda: bot.create_new_sticker_set(
                user_id=ADMIN_USER_ID,
                name=pack_name,
                title=f"Clock pack {pack_index + 1}/{PACK_COUNT}",
                stickers=stickers,
                sticker_type="custom_emoji",
                needs_repainting=True,
            )
        )

        uploaded_count = len(first_batch)
        await db.upsert_clock_pack(pack_index, pack_name, uploaded_count, 0)
        print(f"pack {pack_index}: создан, {uploaded_count} эмодзи")

    remaining = chunk[uploaded_count:]
    for time_key in remaining:
        sticker = _build_input_sticker(pack_index, time_key)

        await _call_with_retry(
            lambda sticker=sticker: bot.add_sticker_to_set(
                user_id=ADMIN_USER_ID,
                name=pack_name,
                sticker=sticker,
            )
        )

        uploaded_count += 1
        await db.upsert_clock_pack(pack_index, pack_name, uploaded_count, 0)
        print(f"pack {pack_index}: {uploaded_count}/{len(chunk)}")
        await asyncio.sleep(UPLOAD_DELAY)

    sticker_set = await _call_with_retry(lambda: bot.get_sticker_set(pack_name))
    for time_key, sticker in zip(chunk, sticker_set.stickers):
        await db.save_clock_emoji(time_key, pack_index, sticker.custom_emoji_id)

    await db.upsert_clock_pack(pack_index, pack_name, len(chunk), 1)
    print(f"pack {pack_index}: ГОТОВ, маппинг сохранён ({len(chunk)} записей)")


async def main():
    if not os.path.isdir(INPUT_DIR):
        print(
            f"Папка {INPUT_DIR}/ не найдена. Сначала запустите generate_emoji_images.py"
        )
        return

    await Tortoise.init(config=TORTOISE_ORM)

    bot = Bot(token=BOT_TOKEN)
    me = await bot.get_me()
    print(f"Паки будут созданы от имени @{me.username}")

    times = all_time_keys()

    for pack_index in range(PACK_COUNT):
        pack_row = await db.get_clock_pack(pack_index)
        if pack_row and pack_row["completed"]:
            print(f"pack {pack_index}: уже готов, пропускаю")
            continue

        chunk = times[pack_index * PACK_SIZE : (pack_index + 1) * PACK_SIZE]
        await _upload_pack(bot, me, pack_index, chunk)

    total_mapped = await db.count_clock_emojis()
    print(f"Итого в таблице соответствия: {total_mapped}/{len(times)}")

    await bot.session.close()
    await Tortoise.close_connections()


if __name__ == "__main__":
    asyncio.run(main())
