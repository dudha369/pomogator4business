import asyncio
import io

from PIL import Image
from aiogram.types import BufferedInputFile, InputStoryContentPhoto

from core.context import CommandContext
from core.registry import command
from core import database as db

_GRID = {
    3: (3, 1),
    6: (3, 2),
    9: (3, 3),
}
_ACTIVE_PERIOD = 86400
_POST_DELAY = 1.0


def split_image(image_bytes, parts):
    rows, cols = _GRID[parts]
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    width, height = image.size
    tile_w = width // cols
    tile_h = height // rows
    image = image.resize((tile_w * cols, tile_h * rows))

    tiles = []
    for row in range(rows):
        for col in range(cols):
            box = (col * tile_w, row * tile_h, (col + 1) * tile_w, (row + 1) * tile_h)
            tile = image.crop(box)
            buffer = io.BytesIO()
            tile.save(buffer, format="JPEG", quality=95)
            tiles.append(buffer.getvalue())
    return tiles


async def _post_tile(bot, connection_id, tile_bytes):
    content = InputStoryContentPhoto.model_construct(
        photo=BufferedInputFile(tile_bytes, filename="story.jpg")
    )
    await bot.post_story(
        business_connection_id=connection_id,
        content=content,
        active_period=_ACTIVE_PERIOD,
    )


async def _post_all(bot, connection_id, tiles):
    for tile_bytes in tiles:
        try:
            await _post_tile(bot, connection_id, tile_bytes)
        except Exception:
            pass
        await asyncio.sleep(_POST_DELAY)


@command(
    name="story", module="story", description="Разрезает фото и публикует как Истории"
)
async def cmd_story(ctx: CommandContext):
    target = ctx.message.reply_to_message
    if not target or not target.photo:
        await ctx.answer(ctx.t("story.usage_reply"))
        return

    raw_parts = ctx.args.strip()
    parts = int(raw_parts) if raw_parts.isdigit() and int(raw_parts) in _GRID else 9

    photo = target.photo[-1]
    file = await ctx.bot.get_file(photo.file_id)
    buffer = await ctx.bot.download_file(file.file_path)
    tiles = split_image(buffer.read(), parts)

    await ctx.delete_command_message()

    if await db.is_autopost_enabled(ctx.connection_id):
        await db.queue_story_tiles(ctx.connection_id, tiles)
        await ctx.answer(ctx.t("story.queued", parts=parts))
        return

    await _post_all(ctx.bot, ctx.connection_id, tiles)
    await ctx.answer(ctx.t("story.published", parts=parts))


@command(
    name="storyautopost",
    module="story",
    description="Включает/выключает автопостинг историй",
)
async def cmd_storyautopost(ctx: CommandContext):
    enabled = await db.toggle_autopost(ctx.connection_id)
    await ctx.delete_command_message()
    status = ctx.t("story.status_on") if enabled else ctx.t("story.status_off")
    await ctx.answer(ctx.t("story.autopost_toggled", status=status))


async def autopost_tick(bot, today: str):
    connections = await db.get_autopost_enabled_connections()
    for connection_id in connections:
        if await db.get_last_post_date(connection_id) == today:
            continue
        tile_bytes = await db.pop_next_tile(connection_id)
        if tile_bytes is None:
            continue
        try:
            await _post_tile(bot, connection_id, tile_bytes)
            await db.set_last_post_date(connection_id, today)
        except Exception:
            pass
